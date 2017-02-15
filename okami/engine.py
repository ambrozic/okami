import asyncio
import logging
import random
import time
from collections import defaultdict

import aiohttp

from okami import constants, loader, signals
from okami.api import Request, Result, Stats, Task
from okami.configuration import settings
from okami.exceptions import (
    OkamiTerminationException, HttpMiddlewareException,
    ItemsPipelineException, TasksPipelineException,
    RequestsPipelineException, ResponsesPipelineException,
    StartupPipelineException, StatsPipelineException
)

log = logging.getLogger(__name__)


class Okami:
    @staticmethod
    def start(name):
        spider = loader.get_spider_class_by_name(name=name)()
        controller = Controller(spider=spider)
        controller.start()

    @staticmethod
    def process(name, url):
        spider = loader.get_spider_class_by_name(name=name)()
        controller = Controller(spider=spider)
        controller.manager.storage.initialise()
        result = asyncio.get_event_loop().run_until_complete(controller.process(task=Task(url=url)))
        items = [item.to_dict() for item in result.items]
        controller.close()
        return items

    @staticmethod
    def serve(address=settings.HTTP_SERVER_ADDRESS):
        loader.get_class(settings.HTTP_SERVER)(address=address).start()


class Manager:
    def __init__(self, name, storage):
        self.name = name
        self.storage = storage
        self.terminate = False
        self.retrials = set()
        self.counters = defaultdict(lambda: defaultdict(lambda: 0))
        self.iterations = 0
        self.event = asyncio.locks.Event()
        self.semaphore = asyncio.locks.Semaphore(value=settings.CONN_MAX_CONCURRENT_REQUESTS)

    def stop(self):
        self.terminate = True
        return self.terminate

    @property
    def running(self):
        return not self.terminate and (bool(self.retrials) or not self.storage.tasks_queued_is_empty())

    async def scheduled(self):
        subset = set(list(self.retrials or [self.storage.get_tasks_queued()])[:1])
        self.retrials -= subset
        return subset

    async def process(self, result):
        self.iterations += 1

        if result.status == constants.status.RETRIAL:
            self.retrials.add(result.task)
            retrials = self.counters["retrials"]
            retrials[result.task] += 1
            if retrials[result.task] >= settings.CONN_MAX_RETRIES:
                raise OkamiTerminationException("CONN_MAX_RETRIES Reached. Terminating!")
            await asyncio.sleep(settings.PAUSE_TIMEOUT)

        if result.status in constants.FAILED:
            self.storage.add_tasks_failed({result.task})
            failed = self.storage.get_tasks_failed()
            if len(failed) >= settings.REQUEST_MAX_FAILED:
                raise OkamiTerminationException("REQUEST_MAX_FAILED Reached. Terminating!")

        if result.tasks:
            self.storage.add_tasks_queued(result.tasks)

        if result.items:
            self.storage.add_info_items_processed(len(result.items))

        if not self.event.is_set():
            self.event.set()


class Controller:
    def __new__(cls, *args, **kwargs):
        asyncio.set_event_loop_policy(settings.EVENT_LOOP_POLICY)
        loop = asyncio.get_event_loop()
        loop.slow_callback_duration = 0.2
        loop.set_debug(settings.DEBUG)
        return super().__new__(cls, *args)

    def __init__(self, spider):
        self.spider = spider
        self.loop = asyncio.get_event_loop()
        self.is_leader = False
        self.session = None
        self.storage = loader.get_class(settings.STORAGE)(name=self.spider.name, **settings.STORAGE_SETTINGS)
        self.throttle = loader.get_class(settings.THROTTLE)(**settings.THROTTLE_SETTINGS)
        self.downloader = loader.get_class(settings.DOWNLOADER)(controller=self)
        self.middleware = Middlewares(controller=self)
        self.pipeline = Pipelines(controller=self)
        self.manager = Manager(name=self.spider.name, storage=self.storage)

    def start(self):
        log.debug("Okami: starting")
        try:
            self.loop.run_until_complete(self.initialise())
            self.loop.run_until_complete(self.run())
        except (KeyboardInterrupt, SystemExit):
            pass
        except Exception as e:
            log.exception(e)
        finally:
            self.close()

    async def initialise(self):
        log.debug("Okami: initialising")
        self.manager.event.clear()
        await asyncio.sleep(random.randint(0, 100) / 1000.0)
        self.is_leader = self.manager.storage.initialise()
        if self.is_leader:
            self.manager.storage.set_info_time_initialised(time.time())
        self.manager.storage.add_tasks_queued({Task(url=url) for url in self.spider.urls.get("start", [])})
        self.spider = await self.pipeline.startup.process(self.spider)

    async def run(self):
        log.debug("Okami: running")
        if self.is_leader:
            self.manager.storage.set_info_time_started(time.time())

        with self.throttle as throttle:
            while self.manager.running:
                for task in await self.manager.scheduled():
                    await asyncio.Task(self.process(task=task))
                    await asyncio.sleep(max(1.0 - (self.manager.iterations * 0.2) ** 2.0, throttle.sleep))

                if not self.manager.event.is_set():
                    await self.manager.event.wait()

    async def process(self, task):
        status, tasks, items = 0, set(), set()
        with (await self.manager.semaphore):
            try:
                request = Request(url=task.url)
                request = await self.pipeline.requests.process(request)
                request = await self.middleware.http.before(request)
                response = await self.downloader.process(request)
                response = await self.middleware.http.after(response)
                response = await self.pipeline.responses.process(response)

                if response.status in constants.HTTP_FAILED:
                    status = response.status
                else:
                    tasks, items = await self.spider.process(task=task, response=response)
                    if tasks:
                        tasks = await self.pipeline.tasks.process(tasks)
                    if items:
                        items = await self.pipeline.items.process(items)

                await self.pipeline.stats.process(stats=await self.stats())

            except (aiohttp.DisconnectedError, aiohttp.ClientError) as e:
                log.exception(e)
                status = constants.status.RETRIAL
                self.session.close()
            except Exception as e:
                log.exception(e)
                status = constants.status.FAILED

            result = Result(status=status, task=task, tasks=tasks, items=items)
            await self.manager.process(result=result)
            return result

    def close(self):
        log.debug("Okami: stopping")
        self.manager.stop()
        try:
            self.loop.run_until_complete(asyncio.gather(*asyncio.Task.all_tasks()))
        except Exception as e:
            log.exception(e)
        finally:
            self.manager.storage.finalise()
            if self.session and not self.session.closed:
                self.session.close()
            if self.loop:
                self.loop.close()
        log.debug("Okami: finished")

    async def stats(self):
        if not self.pipeline.stats.sources:
            return
        return Stats.from_dict({**self.manager.storage.to_dict(), **dict(state=self.throttle.to_dict())})


class Middlewares:
    def __init__(self, controller):
        self.http = HttpMiddleware(controller=controller)


class Middleware:
    """
    Base :class:`Middleware <okami.engine.Middleware>` object

    :param controller: :class:`Controller <okami.engine.Controller>` object
    :ivar sources: merged tuple of registered middleware
    :ivar cached: middleware is lazily loaded and cached
    """

    def __init__(self, controller):
        self.controller = controller
        self.sources = []
        self.cached = []

    @property
    def middleware(self):
        if not self.cached:
            for middleware in self.sources:
                self.cached.append(loader.get_class(middleware)(controller=self.controller))
        return self.cached

    async def before(self, something):
        raise NotImplementedError

    async def after(self, something):
        raise NotImplementedError


class HttpMiddleware(Middleware):
    """
    :class:`HttpMiddleware <okami.engine.HttpMiddleware>` object

    :param controller: :class:`Controller <okami.engine.Controller>` object
    :ivar sources: merged tuple of registered middleware
    """

    def __init__(self, controller):
        super().__init__(controller)
        self.sources = settings.BASE_HTTP_MIDDLEWARE + settings.HTTP_MIDDLEWARE

    async def before(self, request):
        """
        Runs a :class:`Request <okami.api.Request>` object through all registered http middleware.
        Runs for every request/response cycle.

        :param request: :class:`Request <okami.api.Request>` object
        :returns: :class:`Request <okami.api.Request>` object
        """
        try:
            if self.middleware:
                await signals.http_middleware_started.send(sender=self, request=request)
                for middleware in self.middleware:
                    request = await middleware.before(request)
            return request
        except Exception as e:
            raise HttpMiddlewareException(e) from e

    async def after(self, response):
        """
        Runs a :class:`Response <okami.api.Response>` object through all registered http middleware.
        Runs for every request/response cycle.

        :param response: :class:`Response <okami.api.Response>` object
        :returns: :class:`Response <okami.api.Response>` object
        """
        try:
            if self.middleware:
                for middleware in reversed(self.middleware):
                    response = await middleware.after(response)
                await signals.http_middleware_finished.send(sender=self, response=response)
            return response
        except Exception as e:
            raise HttpMiddlewareException(e) from e


class Pipelines:
    def __init__(self, controller):
        self.startup = StartupPipelines(controller=controller)
        self.stats = StatsPipelines(controller=controller)
        self.requests = RequestsPipelines(controller=controller)
        self.responses = ResponsesPipelines(controller=controller)
        self.items = ItemsPipelines(controller=controller)
        self.tasks = TasksPipelines(controller=controller)


class Pipeline:
    """
    Base :class:`Pipeline <okami.engine.Pipeline>` object

    :param controller: :class:`Controller <okami.engine.Controller>` object
    :ivar sources: merged tuple of registered pipelines
    :ivar cached: pipelines are lazily loaded and cached
    """

    def __init__(self, controller):
        self.controller = controller
        self.sources = []
        self.cached = []

    @property
    def pipelines(self):
        if not self.cached:
            for pipeline in self.sources:
                instance = loader.get_class(pipeline)(controller=self.controller)
                self.cached.append(instance)
        return self.cached

    async def process(self, something):
        raise NotImplementedError


class StartupPipelines(Pipeline):
    """
    :class:`StartupPipeline <okami.engine.StartupPipeline>` object

    :param controller: :class:`Controller <okami.engine.Controller>` object
    :ivar sources: merged tuple of registered pipelines
    """

    def __init__(self, controller):
        super().__init__(controller)
        self.sources = settings.BASE_STARTUP_PIPELINE + settings.STARTUP_PIPELINE

    async def process(self, spider):
        """
        Runs a :class:`Spider <okami.Spider>` object through all registered startup pipelines.
        Only runs once, at start.

        :param spider: :class:`Spider <okami.Spider>` object
        :returns: :class:`Spider <okami.Spider>` object
        """
        try:
            if self.pipelines:
                await signals.startup_pipeline_started.send(sender=self, spider=spider)
                for pipeline in self.pipelines:
                    spider = await pipeline.process(spider)
                await signals.startup_pipeline_finished.send(sender=self, spider=spider)
            return spider
        except Exception as e:
            raise StartupPipelineException(e) from e


class StatsPipelines(Pipeline):
    """
    :class:`StatsPipeline <okami.engine.StatsPipeline>` object

    :param controller: :class:`Controller <okami.engine.Controller>` object
    :ivar sources: merged tuple of registered pipelines
    """

    def __init__(self, controller):
        super().__init__(controller)
        self.sources = settings.BASE_STATS_PIPELINE + settings.STATS_PIPELINE

    async def process(self, stats):
        """
        Runs a :class:`Stats <okami.api.Stats>` object through all registered stats pipelines.
        Runs for every request or less, depending on **settings.STATS_PIPELINE_FREQUENCY** setting.

        :param stats: :class:`Stats <okami.api.Stats>` object
        :returns: :class:`Stats <okami.api.Stats>` object
        """
        try:
            if not self.controller.manager.iterations % settings.STATS_PIPELINE_FREQUENCY:
                if self.pipelines:
                    await signals.stats_pipeline_started.send(sender=self, stats=stats)
                    for pipeline in self.pipelines:
                        stats = await pipeline.process(stats)
                    await signals.stats_pipeline_finished.send(sender=self, stats=stats)
            return stats
        except Exception as e:
            raise StatsPipelineException(e) from e


class RequestsPipelines(Pipeline):
    """
    :class:`RequestsPipelines <okami.engine.RequestsPipelines>` object

    :param controller: :class:`Controller <okami.engine.Controller>` object
    :ivar sources: merged tuple of registered pipelines
    """

    def __init__(self, controller):
        super().__init__(controller)
        self.sources = settings.BASE_REQUESTS_PIPELINE + settings.REQUESTS_PIPELINE

    async def process(self, request):
        """
        Runs a :class:`Request <okami.api.Request>` object through all registered requests pipelines.
        Runs for every request.

        :param request: :class:`Request <okami.api.Request>` object
        :returns: :class:`Request <okami.api.Request>` object
        """
        try:
            if self.pipelines:
                await signals.requests_pipeline_started.send(sender=self, request=request)
                for pipeline in self.pipelines:
                    request = await pipeline.process(request)
                await signals.requests_pipeline_finished.send(sender=self, request=request)
            return request
        except Exception as e:
            raise RequestsPipelineException(e) from e


class ResponsesPipelines(Pipeline):
    """
    :class:`ResponsesPipelines <okami.engine.ResponsesPipelines>` object

    :param controller: :class:`Controller <okami.engine.Controller>` object
    :ivar sources: merged tuple of registered pipelines
    """

    def __init__(self, controller):
        super().__init__(controller)
        self.sources = settings.BASE_RESPONSES_PIPELINE + settings.RESPONSES_PIPELINE

    async def process(self, response):
        """
        Runs a :class:`Response <okami.api.Response>` object through all registered responses pipelines.
        Runs for every request.

        :param response: :class:`Response <okami.api.Response>` object
        :returns: :class:`Response <okami.api.Response>` object
        """
        try:
            if self.pipelines:
                await signals.responses_pipeline_started.send(sender=self, response=response)
                for pipeline in self.pipelines:
                    response = await pipeline.process(response)
                await signals.responses_pipeline_finished.send(sender=self, response=response)
            return response
        except Exception as e:
            raise ResponsesPipelineException(e) from e


class ItemsPipelines(Pipeline):
    """
    :class:`ItemsPipelines <okami.engine.ItemsPipelines>` object

    :param controller: :class:`Controller <okami.engine.Controller>` object
    :ivar sources: merged tuple of registered pipelines
    """

    def __init__(self, controller):
        super().__init__(controller)
        self.sources = settings.BASE_ITEMS_PIPELINE + settings.ITEMS_PIPELINE

    async def process(self, items):
        """
        Runs a list of Item objects through all registered items pipelines.
        Runs for every request.

        :param items: (list) of :class:`Item <okami.Item>` objects
        :returns: (list) of :class:`Item <okami.Item>` objects
        """
        try:
            if self.pipelines:
                await signals.items_pipeline_started.send(sender=self, items=items)
                for pipeline in self.pipelines:
                    items = await pipeline.process(items)
                await signals.items_pipeline_finished.send(sender=self, items=items)
            return items
        except Exception as e:
            raise ItemsPipelineException(e) from e


class TasksPipelines(Pipeline):
    """
    :class:`TasksPipelines <okami.engine.TasksPipelines>` object

    :param controller: :class:`Controller <okami.engine.Controller>` object
    :ivar sources: merged tuple of registered pipelines
    """

    def __init__(self, controller):
        super().__init__(controller)
        self.sources = settings.BASE_TASKS_PIPELINE + settings.TASKS_PIPELINE

    async def process(self, tasks):
        """
        Runs a list of :class:`Task <okami.Task>` objects through all registered tasks pipelines.
        Runs for every request.

        :param tasks: (list) of :class:`Task <okami.Task>` objects
        :returns: (list) of :class:`Task <okami.Task>` objects
        """
        try:
            if self.pipelines:
                await signals.tasks_pipeline_started.send(sender=self, tasks=tasks)
                for pipeline in self.pipelines:
                    tasks = await pipeline.process(tasks)
                await signals.tasks_pipeline_finished.send(sender=self, tasks=tasks)
            return tasks
        except Exception as e:
            raise TasksPipelineException(e) from e

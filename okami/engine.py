import asyncio
import logging
import time
from collections import defaultdict

import aiohttp

from okami import constants, loader, settings, signals
from okami.api import Request, Result, Stats, Task
from okami.exceptions import (
    HttpMiddlewareException,
    ItemsPipelineException,
    OkamiTerminationException,
    SpiderMiddlewareException,
    StartupPipelineException,
    TasksPipelineException,
)

log = logging.getLogger(__name__)

asyncio.set_event_loop_policy(settings.EVENT_LOOP_POLICY)


class Okami:
    @staticmethod
    def start(name):
        spider = loader.get_spider_class_by_name(name=name)()
        asyncio.get_event_loop().run_until_complete(Controller(spider=spider).start())

    @staticmethod
    def process(name, url):
        loop = asyncio.get_event_loop()
        spider = loader.get_spider_class_by_name(name=name)()
        controller = Controller(spider=spider)
        loop.run_until_complete(controller.initialise())
        result = loop.run_until_complete(controller.process(task=Task(url=url)))
        items = [item.to_dict() for item in result.items]
        loop.run_until_complete(controller.finalise())
        return items

    @staticmethod
    def serve(address=settings.HTTP_SERVER_ADDRESS):
        loader.get_class(settings.HTTP_SERVER)(address=address).start()


class Controller:
    def __init__(self, spider):
        if settings.DEBUG:
            loop = asyncio.get_event_loop()
            loop.set_debug(enabled=settings.DEBUG)
            loop.slow_callback_duration = settings.ASYNC_SLOW_CALLBACK_DURATION

        self.spider = spider
        self.stats = Stats(controller=self)
        self.session = None
        self.storage = loader.get_class(settings.STORAGE)(name=self.spider.name, **settings.STORAGE_SETTINGS)
        self.throttle = loader.get_class(settings.THROTTLE)(**settings.THROTTLE_SETTINGS)
        self.downloader = loader.get_class(settings.DOWNLOADER)(controller=self)
        self.middleware = Middlewares(controller=self)
        self.pipeline = Pipelines(controller=self)
        self.manager = Manager(name=self.spider.name, storage=self.storage)

    async def initialise(self):
        log.debug("Okami: initialising")
        await self.pipeline.initialise()
        await self.middleware.initialise()
        self.spider = await self.pipeline.startup.process(spider=self.spider)
        self.manager.event.clear()
        self.manager.storage.add_tasks_queued({Task(url=url) for url in self.spider.urls.get("start", [])})

    async def start(self):
        log.debug("Okami: starting")
        try:
            await self.initialise()
            await self.run()
        except (KeyboardInterrupt, SystemExit):
            pass
        except Exception as e:
            log.exception(e)
        finally:
            await self.finalise()

    async def run(self):
        log.debug("Okami: running")
        self.manager.storage.set_info_time_started(time.time())

        with self.throttle as throttle:
            while self.manager.running:
                for task in await self.manager.scheduled():
                    await asyncio.Task(self.process(task=task))
                    await asyncio.sleep(throttle.sleep)

                if not self.manager.event.is_set():
                    await self.manager.event.wait()

    async def process(self, task):
        status, tasks, items = 0, set(), set()
        with (await self.manager.semaphore):
            try:
                request = Request(url=task.url)
                request = await self.middleware.http.before(request=request)
                response = await self.downloader.process(request=request)
                response = await self.middleware.http.after(response=response)

                if response.status in constants.HTTP_FAILED:
                    status = response.status
                else:
                    response = await self.middleware.spider.before(task=task, response=response)
                    tasks, items = await self.spider.process(task=task, response=response)
                    tasks, items = await self.middleware.spider.after(
                        task=task, response=response, tasks=tasks, items=items
                    )
                    if tasks:
                        tasks = await self.pipeline.tasks.process(tasks=tasks)
                    if items:
                        items = await self.pipeline.items.process(items=items)

            except aiohttp.ClientError as e:
                log.exception(e)
                status = constants.status.RETRIAL
                await self.session.close()
            except Exception as e:
                log.exception(e)
                status = constants.status.FAILED

            result = Result(status=status, task=task, tasks=tasks, items=items)
            await self.manager.process(result=result)
            return result

    async def finalise(self):
        log.debug("Okami: finalising")
        await self.manager.stop()
        if self.session and not self.session.closed:
            await self.session.close()
        await self.pipeline.finalise()
        await self.middleware.finalise()
        log.debug("Okami: finished")


class Manager:
    def __init__(self, name, storage):
        self.name = name
        self.storage = storage
        self.terminate = False
        self.retrials = set()
        self.counters = defaultdict(lambda: defaultdict(lambda: 0))
        self.iterations = 0
        self.event = asyncio.Event()
        self.semaphore = asyncio.Semaphore(value=settings.CONN_MAX_CONCURRENT_REQUESTS)

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

    async def stop(self):
        self.terminate = True
        return self.terminate


class Middlewares:
    def __init__(self, controller):
        self.http = HttpMiddleware(controller=controller)
        self.spider = SpiderMiddleware(controller=controller)

    async def initialise(self):
        for middleware in [self.http, self.spider]:
            await middleware.initialise()

    async def finalise(self):
        for middleware in [self.http, self.spider]:
            await middleware.finalise()


class Middleware:
    """
    Base Middleware <okami.engine.Middleware>

    :param controller: Controller <okami.engine.Controller>
    :ivar sources: merged tuple of registered middleware
    :ivar cached: middleware is lazily loaded and cached
    """

    def __init__(self, controller):
        self.controller = controller
        self.sources = []
        self.cached = []

    @property
    def middlewares(self):
        if not self.cached:
            for middleware in self.sources:
                self.cached.append(loader.get_class(middleware)(controller=self.controller))
        return self.cached

    async def initialise(self):
        raise NotImplementedError

    async def before(self, **kwargs):
        raise NotImplementedError

    async def after(self, **kwargs):
        raise NotImplementedError

    async def finalise(self):
        raise NotImplementedError


class HttpMiddleware(Middleware):
    """
    HttpMiddleware <okami.engine.HttpMiddleware>

    :param controller: Controller <okami.engine.Controller>
    :ivar sources: merged tuple of registered http middleware
    """

    def __init__(self, controller):
        super().__init__(controller)
        self.sources = settings.BASE_HTTP_MIDDLEWARE + settings.HTTP_MIDDLEWARE

    async def initialise(self):
        """
        Initialises all registered http middleware at the beginning of scraping process.
        """
        try:
            if self.middlewares:
                for middleware in self.middlewares:
                    await middleware.initialise()
                    await signals.http_middleware_initialised.send(sender=middleware)
        except Exception as e:
            raise HttpMiddlewareException(e) from e

    async def before(self, request):
        """
        Runs passed Request <okami.Request> through all registered http middleware.
        Runs for every request/response cycle.

        :param request: Request <okami.Request>
        :returns: Request <okami.Request>
        """
        try:
            if self.middlewares:
                for middleware in self.middlewares:
                    try:
                        request = await middleware.before(request=request)
                    except NotImplementedError:
                        request = request
                    await signals.http_middleware_started.send(sender=middleware, request=request)
            return request
        except Exception as e:
            raise HttpMiddlewareException(e) from e

    async def after(self, response):
        """
        Runs passed Response <okami.Response> through all registered http middleware.
        Runs for every request/response cycle.

        :param response: Response <okami.Response>
        :returns: Response <okami.Response>
        """
        try:
            if self.middlewares:
                for middleware in reversed(self.middlewares):
                    try:
                        response = await middleware.after(response=response)
                    except NotImplementedError:
                        response = response
                    await signals.http_middleware_finished.send(sender=middleware, response=response)
            return response
        except Exception as e:
            raise HttpMiddlewareException(e) from e

    async def finalise(self):
        """
        Finalises all registered http middleware at the end of scraping process.
        """
        try:
            if self.middlewares:
                for middleware in reversed(self.middlewares):
                    await middleware.finalise()
                    await signals.http_middleware_finalised.send(sender=middleware)
        except Exception as e:
            raise HttpMiddlewareException(e) from e


class SpiderMiddleware(Middleware):
    """
    SpiderMiddleware <okami.engine.SpiderMiddleware>

    :param controller: Controller <okami.engine.Controller>
    :ivar sources: merged tuple of registered spider middleware
    """

    def __init__(self, controller):
        super().__init__(controller)
        self.sources = settings.BASE_SPIDER_MIDDLEWARE + settings.SPIDER_MIDDLEWARE

    async def initialise(self):
        """
        Initialises all registered spider middleware at the beginning of scraping process.
        """
        try:
            if self.middlewares:
                for middleware in self.middlewares:
                    await middleware.initialise()
                    await signals.spider_middleware_initialised.send(sender=middleware)
        except Exception as e:
            raise SpiderMiddlewareException(e) from e

    async def before(self, task, response):
        """
        Runs passed objects through all registered spider middleware.
        Runs for every spider scraping cycle.

        :param task: Task <okami.Task>
        :param response: Response <okami.Response>
        :returns: Response <okami.Response>
        """
        try:
            if self.middlewares:
                for middleware in self.middlewares:
                    try:
                        response = await middleware.before(task=task, response=response)
                    except NotImplementedError:
                        response = response
                    await signals.spider_middleware_started.send(sender=middleware, task=task, response=response)
            return response
        except Exception as e:
            raise SpiderMiddlewareException(e) from e

    async def after(self, task, response, tasks, items):
        """
        Runs passed objects through all registered spider middleware.
        Runs for every spider scraping cycle.

        :param task: Task <okami.Task>
        :param response: Response <okami.Response>
        :param tasks: Set[Task <okami.Task>]
        :param items: List[Item <okami.Item>]
        :returns: tuple of (Set[Task <okami.Task>], List[Item <okami.Item>])
        """
        try:
            if self.middlewares:
                for middleware in reversed(self.middlewares):
                    try:
                        tasks, items = await middleware.after(task=task, response=response, tasks=tasks, items=items)
                    except NotImplementedError:
                        tasks, items = tasks, items
                    await signals.spider_middleware_finished.send(
                        sender=middleware, task=task, response=response, tasks=tasks, items=items
                    )
            return tasks, items
        except Exception as e:
            raise SpiderMiddlewareException(e) from e

    async def finalise(self):
        """
        Finalises all registered spider middleware at the end of scraping process.
        """
        try:
            if self.middlewares:
                for middleware in reversed(self.middlewares):
                    await middleware.finalise()
                    await signals.spider_middleware_finalised.send(sender=middleware)
        except Exception as e:
            raise SpiderMiddlewareException(e) from e


class Pipelines:
    def __init__(self, controller):
        self.startup = StartupPipeline(controller=controller)
        self.items = ItemsPipeline(controller=controller)
        self.tasks = TasksPipeline(controller=controller)

    async def initialise(self):
        for pipeline in [self.startup, self.items, self.tasks]:
            await pipeline.initialise()

    async def finalise(self):
        for pipeline in [self.startup, self.items, self.tasks]:
            await pipeline.finalise()


class Pipeline:
    """
    Base Pipeline <okami.engine.Pipeline>

    :param controller: Controller <okami.engine.Controller>
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

    async def initialise(self):
        raise NotImplementedError

    async def process(self, something):
        raise NotImplementedError

    async def finalise(self):
        raise NotImplementedError


class StartupPipeline(Pipeline):
    """
    StartupPipeline <okami.engine.StartupPipeline>

    :param controller: Controller <okami.engine.Controller>
    :ivar sources: merged tuple of registered pipelines
    """

    def __init__(self, controller):
        super().__init__(controller)
        self.sources = settings.BASE_STARTUP_PIPELINE + settings.STARTUP_PIPELINE

    async def initialise(self):
        """
        Initialises all registered startup pipelines at the beginning of scraping process.
        """
        try:
            if self.pipelines:
                for pipeline in self.pipelines:
                    await pipeline.initialise()
                    await signals.startup_pipeline_initialised.send(sender=pipeline)
        except Exception as e:
            raise StartupPipelineException(e) from e

    async def process(self, spider):
        """
        Runs a Spider <okami.Spider> through all registered startup pipelines.
        Only runs once, at start.

        :param spider: Spider <okami.Spider>
        :returns: Spider <okami.Spider>
        """
        try:
            if self.pipelines:
                for pipeline in self.pipelines:
                    await signals.startup_pipeline_started.send(sender=pipeline, spider=spider)
                    try:
                        spider = await pipeline.process(spider=spider)
                    except NotImplementedError:
                        spider = spider
                    await signals.startup_pipeline_finished.send(sender=pipeline, spider=spider)
            return spider
        except Exception as e:
            raise StartupPipelineException(e) from e

    async def finalise(self):
        """
        Finalises all registered startup pipelines at the end of scraping process.
        """
        try:
            if self.pipelines:
                for pipeline in self.pipelines:
                    await pipeline.finalise()
                    await signals.startup_pipeline_finalised.send(sender=pipeline)
        except Exception as e:
            raise StartupPipelineException(e) from e


class ItemsPipeline(Pipeline):
    """
    ItemsPipeline <okami.engine.ItemsPipeline>

    :param controller: Controller <okami.engine.Controller>
    :ivar sources: merged tuple of registered pipelines
    """

    def __init__(self, controller):
        super().__init__(controller)
        self.sources = settings.BASE_ITEMS_PIPELINE + settings.ITEMS_PIPELINE

    async def initialise(self):
        """
        Initialises all registered items pipelines at the beginning of scraping process.
        """
        try:
            if self.pipelines:
                for pipeline in self.pipelines:
                    await pipeline.initialise()
                    await signals.items_pipeline_initialised.send(sender=pipeline)
        except Exception as e:
            raise ItemsPipelineException(e) from e

    async def process(self, items):
        """
        Runs a List[Item <okami.Item>] through all registered items pipelines.
        Runs for every request.

        :param items: List[Item <okami.Item>]
        :returns: List[Item <okami.Item>]
        """
        try:
            if self.pipelines:
                for pipeline in self.pipelines:
                    await signals.items_pipeline_started.send(sender=pipeline, items=items)
                    try:
                        items = await pipeline.process(items=items)
                    except NotImplementedError:
                        items = items
                    await signals.items_pipeline_finished.send(sender=pipeline, items=items)
            return items
        except Exception as e:
            raise ItemsPipelineException(e) from e

    async def finalise(self):
        """
        Finalises all registered tasks pipelines at the end of scraping process.
        """
        try:
            if self.pipelines:
                for pipeline in self.pipelines:
                    await pipeline.finalise()
                    await signals.items_pipeline_finalised.send(sender=pipeline)
        except Exception as e:
            raise ItemsPipelineException(e) from e


class TasksPipeline(Pipeline):
    """
    TasksPipeline <okami.engine.TasksPipeline>

    :param controller: Controller <okami.engine.Controller>
    :ivar sources: merged tuple of registered pipelines
    """

    def __init__(self, controller):
        super().__init__(controller)
        self.sources = settings.BASE_TASKS_PIPELINE + settings.TASKS_PIPELINE

    async def initialise(self):
        """
        Initialises all registered tasks pipelines at the beginning of scraping process.
        """
        try:
            if self.pipelines:
                for pipeline in self.pipelines:
                    await pipeline.initialise()
                    await signals.tasks_pipeline_initialised.send(sender=pipeline)
        except Exception as e:
            raise TasksPipelineException(e) from e

    async def process(self, tasks):
        """
        Runs a List[Task <okami.Task>`] through all registered tasks pipelines.
        Runs for every request.

        :param tasks: Set[Task <okami.Task>`]
        :returns: Set[Task <okami.Task>`]
        """
        try:
            if self.pipelines:
                for pipeline in self.pipelines:
                    await signals.tasks_pipeline_started.send(sender=pipeline, tasks=tasks)
                    try:
                        tasks = await pipeline.process(tasks=tasks)
                    except NotImplementedError:
                        tasks = tasks
                    await signals.tasks_pipeline_finished.send(sender=pipeline, tasks=tasks)
            return tasks
        except Exception as e:
            raise TasksPipelineException(e) from e

    async def finalise(self):
        """
        Finalises all registered tasks pipelines at the end of scraping process.
        """
        try:
            if self.pipelines:
                for pipeline in self.pipelines:
                    await pipeline.finalise()
                    await signals.tasks_pipeline_finalised.send(sender=pipeline)
        except Exception as e:
            raise TasksPipelineException(e) from e

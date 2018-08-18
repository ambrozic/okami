import asyncio
from unittest import mock

import aiohttp
import pytest

from okami import constants, exceptions, settings
from okami.api import Downloader, Request, Response, Result, Task, Throttle
from okami.engine import (
    Controller,
    HttpMiddleware,
    ItemsPipeline,
    Manager,
    Middleware,
    Middlewares,
    Okami,
    Pipeline,
    Pipelines,
    SpiderMiddleware,
    StartupPipeline,
    TasksPipeline,
)
from okami.exceptions import NoSuchSpiderException
from tests.factory import Factory


def test_okami_start(coro):
    controller = mock.Mock()
    controller.start = mock.Mock(side_effect=coro(mock.Mock()))

    with mock.patch("okami.engine.Controller", return_value=controller):
        assert 0 == controller.start.call_count
        Okami.start(name="example.com")
        assert 1 == controller.start.call_count

        with pytest.raises(NoSuchSpiderException):
            Okami.start(name="test")
            assert 2 == controller.start.call_count


def test_okami_process(factory: Factory, coro):
    controller = mock.Mock()
    controller.initialise = mock.Mock(side_effect=coro(mock.Mock()))
    items = [factory.obj.product.create(), factory.obj.product.create()]
    tasks = {Task(url="url1"), Task(url="url2")}
    controller.process = mock.Mock(
        side_effect=coro(
            mock.Mock(side_effect=[Result(status="status", task="task", tasks=tasks, items=items)])
        )
    )
    controller.finalise = mock.Mock(side_effect=coro(mock.Mock()))

    with mock.patch("okami.engine.Controller", return_value=controller):
        assert 0 == controller.initialise.call_count
        assert 0 == controller.process.call_count
        assert 0 == controller.finalise.call_count
        assert [i.to_dict() for i in items] == Okami.process(name="example.com", url="url")
        assert 1 == controller.initialise.call_count
        assert 1 == controller.process.call_count
        assert 1 == controller.finalise.call_count


def test_okami_serve():
    server = mock.Mock()
    server.start = mock.Mock()
    with mock.patch("okami.server.Server", return_value=server):
        Okami.serve(address="address:port")
        assert 1 == server.start.call_count


def test_controller___init__(factory: Factory):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)

    assert type(asyncio.get_event_loop_policy()) == asyncio.unix_events._UnixDefaultEventLoopPolicy
    assert asyncio.get_event_loop().get_debug() is False
    assert asyncio.get_event_loop().slow_callback_duration == 0.1
    assert controller.spider is spider

    assert controller.session is None
    assert isinstance(controller.throttle, Throttle)

    assert isinstance(controller.downloader, Downloader)
    assert controller.downloader.controller is controller

    assert isinstance(controller.middleware, Middlewares)
    assert isinstance(controller.middleware.http, HttpMiddleware)
    assert isinstance(controller.middleware.spider, SpiderMiddleware)

    assert isinstance(controller.pipeline, Pipelines)
    assert isinstance(controller.pipeline.startup, StartupPipeline)
    assert isinstance(controller.pipeline.items, ItemsPipeline)
    assert isinstance(controller.pipeline.tasks, TasksPipeline)

    assert isinstance(controller.manager, Manager)
    assert controller.manager.name == spider.name
    assert controller.manager.storage is controller.storage

    with factory.settings as s:
        s.set(dict(DEBUG=True, ASYNC_SLOW_CALLBACK_DURATION=0.5))
        Controller(spider=spider)
        assert asyncio.get_event_loop().get_debug() is True
        assert asyncio.get_event_loop().slow_callback_duration == 0.5


@pytest.mark.asyncio
async def test_controller_initialise(factory: Factory, coro):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    controller.pipeline.initialise = mock.Mock(side_effect=coro(mock.Mock()))
    controller.pipeline.startup.process = mock.Mock(side_effect=coro(mock.Mock(return_value=spider)))
    controller.middleware.initialise = mock.Mock(side_effect=coro(mock.Mock()))
    controller.manager.event.clear = mock.Mock()
    controller.manager.storage.add_tasks_queued = mock.Mock()
    await controller.initialise()
    assert controller.pipeline.initialise.call_count == 1
    assert controller.pipeline.startup.process.call_count == 1
    assert controller.pipeline.startup.process.call_args == mock.call(spider=spider)
    assert controller.middleware.initialise.call_count == 1
    assert controller.manager.event.clear.call_count == 1
    assert controller.manager.storage.add_tasks_queued.call_count == 1


@pytest.mark.asyncio
async def test_controller_start(factory: Factory, coro):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    controller.initialise = mock.Mock(side_effect=coro(mock.Mock()))
    controller.run = mock.Mock(side_effect=coro(mock.Mock()))
    controller.finalise = mock.Mock(side_effect=coro(mock.Mock()))
    await controller.start()
    assert controller.initialise.call_count == 1
    assert controller.run.call_count == 1
    assert controller.finalise.call_count == 1

    for e in [KeyboardInterrupt, SystemExit, Exception]:
        controller.run = mock.Mock(side_effect=e)
        await controller.start()


@pytest.mark.asyncio
async def test_controller_run(factory: Factory, coro):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    controller.process = mock.Mock(side_effect=coro(mock.Mock()))
    manager = mock.Mock(side_effect=coro(mock.Mock()))
    manager.__class__.running = mock.PropertyMock(side_effect=[True, False])
    controller.manager = manager
    controller.manager.scheduled = mock.Mock(side_effect=coro(mock.Mock(return_value=[object()])))
    controller.manager.storage.set_info_time_started = mock.Mock()
    controller.manager.event.is_set = mock.Mock(return_value=False)
    controller.manager.event.wait = mock.Mock(side_effect=coro(mock.Mock()))
    await controller.run()
    assert controller.process.call_count == 1
    assert controller.manager.storage.set_info_time_started.call_count == 1
    assert controller.manager.event.is_set.call_count == 1
    assert controller.manager.event.wait.call_count == 1

    controller.manager.reset_mock()
    manager.__class__.running = mock.PropertyMock(side_effect=[True, False])
    controller.manager.event.is_set = mock.Mock(return_value=True)
    await controller.run()
    assert controller.process.call_count == 2
    assert controller.manager.storage.set_info_time_started.call_count == 1
    assert controller.manager.event.is_set.call_count == 1
    assert controller.manager.event.wait.call_count == 0


@pytest.mark.parametrize("status", [200, 201, 301, 302])
@pytest.mark.asyncio
async def test_controller_process(factory: Factory, coro, status):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    request = Request(url="url")
    response = mock.Mock(status=status)
    task = mock.Mock()
    tasks = {Task(url="url1"), Task(url="url2")}
    items = [[factory.obj.product.create(), factory.obj.product.create()]]

    controller.middleware.http.before = mock.Mock(side_effect=coro(mock.Mock(return_value=request)))
    controller.downloader.process = mock.Mock(side_effect=coro(mock.Mock(return_value=response)))
    controller.middleware.http.after = mock.Mock(side_effect=coro(mock.Mock(return_value=response)))
    controller.middleware.spider.before = mock.Mock(side_effect=coro(mock.Mock(return_value=response)))
    controller.spider.process = mock.Mock(side_effect=coro(mock.Mock(return_value=(tasks, items))))
    controller.middleware.spider.after = mock.Mock(side_effect=coro(mock.Mock(return_value=(tasks, items))))
    controller.pipeline.tasks.process = mock.Mock(side_effect=coro(mock.Mock(return_value=tasks)))
    controller.pipeline.items.process = mock.Mock(side_effect=coro(mock.Mock(return_value=items)))

    result = await controller.process(task=task)
    assert result.status == 0
    assert result.task is task
    assert result.tasks is tasks
    assert result.items is items
    assert controller.middleware.http.before.call_count == 1
    assert controller.downloader.process.call_count == 1
    assert controller.downloader.process.call_args == mock.call(request=request)
    assert controller.middleware.http.after.call_count == 1
    assert controller.middleware.http.after.call_args == mock.call(response=response)

    assert controller.middleware.spider.before.call_count == 1
    assert controller.middleware.spider.before.call_args == mock.call(task=task, response=response)
    assert controller.spider.process.call_count == 1
    assert controller.spider.process.call_args == mock.call(task=task, response=response)
    assert controller.middleware.spider.after.call_count == 1
    assert controller.middleware.spider.after.call_args == mock.call(
        task=task, response=response, tasks=tasks, items=items
    )
    assert controller.pipeline.tasks.process.call_count == 1
    assert controller.pipeline.tasks.process.call_args == mock.call(tasks=tasks)
    assert controller.pipeline.items.process.call_count == 1
    assert controller.pipeline.items.process.call_args == mock.call(items=items)


@pytest.mark.parametrize("status", constants.HTTP_FAILED)
@pytest.mark.asyncio
async def test_controller_process_http_failed(factory: Factory, coro, status):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    request = Request(url="url")
    response = mock.Mock(status=status)
    task = mock.Mock()
    tasks = {Task(url="url1"), Task(url="url2")}
    items = [[factory.obj.product.create(), factory.obj.product.create()]]

    controller.middleware.http.before = mock.Mock(side_effect=coro(mock.Mock(return_value=request)))
    controller.downloader.process = mock.Mock(side_effect=coro(mock.Mock(return_value=response)))
    controller.middleware.http.after = mock.Mock(side_effect=coro(mock.Mock(return_value=response)))
    controller.middleware.spider.before = mock.Mock(side_effect=coro(mock.Mock(return_value=response)))
    controller.spider.process = mock.Mock(side_effect=coro(mock.Mock(return_value=(tasks, items))))
    controller.middleware.spider.after = mock.Mock(side_effect=coro(mock.Mock(return_value=(tasks, items))))
    controller.pipeline.tasks.process = mock.Mock(side_effect=coro(mock.Mock(return_value=tasks)))
    controller.pipeline.items.process = mock.Mock(side_effect=coro(mock.Mock(return_value=items)))

    result = await controller.process(task=task)
    assert result.status == status, status
    assert result.task is task
    assert result.tasks == set()
    assert result.items == set()
    assert controller.middleware.http.before.call_count == 1
    assert controller.downloader.process.call_count == 1
    assert controller.middleware.http.after.call_count == 1
    assert controller.middleware.spider.before.call_count == 0
    assert controller.spider.process.call_count == 0
    assert controller.middleware.spider.after.call_count == 0
    assert controller.pipeline.tasks.process.call_count == 0
    assert controller.pipeline.items.process.call_count == 0


@pytest.mark.parametrize(
    "exception,status", [(aiohttp.ClientError, constants.status.RETRIAL), (Exception, constants.status.FAILED)]
)
@pytest.mark.asyncio
async def test_controller_process_exceptions(factory: Factory, coro, exception, status):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    request = Request(url="url")
    response = mock.Mock(status=200)
    task = mock.Mock()
    tasks = {Task(url="url1"), Task(url="url2")}
    items = [[factory.obj.product.create(), factory.obj.product.create()]]

    controller.session = mock.Mock()
    controller.session.close = mock.Mock(side_effect=coro(mock.Mock()))
    controller.manager.process = mock.Mock(side_effect=coro(mock.Mock()))
    controller.middleware.http.before = mock.Mock(side_effect=coro(mock.Mock(return_value=request)))
    controller.downloader.process = mock.Mock(side_effect=coro(mock.Mock(side_effect=exception)))
    controller.middleware.http.after = mock.Mock(side_effect=coro(mock.Mock(return_value=response)))
    controller.middleware.spider.before = mock.Mock(side_effect=coro(mock.Mock(return_value=response)))
    controller.spider.process = mock.Mock(side_effect=coro(mock.Mock(return_value=(tasks, items))))
    controller.middleware.spider.after = mock.Mock(side_effect=coro(mock.Mock(return_value=(tasks, items))))
    controller.pipeline.tasks.process = mock.Mock(side_effect=coro(mock.Mock(return_value=tasks)))
    controller.pipeline.items.process = mock.Mock(side_effect=coro(mock.Mock(return_value=items)))

    result = await controller.process(task=task)
    assert result.status == status, (exception, status)
    assert result.task is task
    assert result.tasks == set()
    assert result.items == set()
    assert controller.middleware.http.before.call_count == 1
    assert controller.downloader.process.call_count == 1
    assert controller.middleware.http.after.call_count == 0
    assert controller.middleware.spider.before.call_count == 0
    assert controller.spider.process.call_count == 0
    assert controller.middleware.spider.after.call_count == 0
    assert controller.pipeline.tasks.process.call_count == 0
    assert controller.pipeline.items.process.call_count == 0


@pytest.mark.asyncio
async def test_controller_finalise(factory: Factory, coro):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)

    controller.session = mock.Mock(side_effect=coro(mock.Mock()))
    controller.session.close = mock.Mock(side_effect=coro(mock.Mock()))
    controller.session.__class__.closed = mock.PropertyMock(side_effect=[False, True])
    controller.manager.stop = mock.Mock(side_effect=coro(mock.Mock()))
    controller.pipeline.finalise = mock.Mock(side_effect=coro(mock.Mock()))
    controller.middleware.finalise = mock.Mock(side_effect=coro(mock.Mock()))

    await controller.finalise()
    assert controller.manager.stop.call_count == 1
    assert controller.session.close.call_count == 1
    assert controller.pipeline.finalise.call_count == 1
    assert controller.middleware.finalise.call_count == 1

    await controller.finalise()
    assert controller.manager.stop.call_count == 2
    assert controller.session.close.call_count == 1
    assert controller.pipeline.finalise.call_count == 2
    assert controller.middleware.finalise.call_count == 2


def test_manager___init__():
    storage = mock.Mock()
    manager = Manager(name="name", storage=storage)
    assert manager.name == "name"
    assert manager.storage is storage
    assert manager.terminate is False
    assert manager.retrials == set()
    assert manager.counters == dict()
    assert manager.iterations == 0
    assert manager.event.__class__ is asyncio.Event
    assert manager.semaphore.__class__ is asyncio.Semaphore
    assert manager.semaphore._value == settings.CONN_MAX_CONCURRENT_REQUESTS


@pytest.mark.parametrize(
    "queue,terminate,retrials,running,calls", [
        (True, False, {5}, True, 0),
        (True, True, {5}, False, 0),
        (True, False, set(), False, 1),
        (True, False, {5}, True, 0),
        (False, False, set(), True, 1),
        (True, False, set(), False, 1),
    ]
)
def test_manager_running(queue, terminate, retrials, running, calls):
    storage = mock.Mock()
    storage.tasks_queued_is_empty = mock.Mock(side_effect=[queue])

    manager = Manager(name="name", storage=storage)
    manager.terminate = terminate
    manager.retrials = retrials
    assert manager.running is running, (terminate, retrials, running, calls)
    assert storage.tasks_queued_is_empty.call_count == calls, (terminate, retrials, running, calls)


@pytest.mark.asyncio
async def test_manager_scheduled():
    storage = mock.Mock()
    storage.get_tasks_queued = mock.Mock(side_effect=[222, 333])

    manager = Manager(name="name", storage=storage)
    manager.retrials = {11, 22}

    assert {11} == await manager.scheduled()
    assert storage.get_tasks_queued.call_count == 0
    assert {22} == await manager.scheduled()
    assert storage.get_tasks_queued.call_count == 0

    manager.retrials = set()
    assert {222} == await manager.scheduled()
    assert storage.get_tasks_queued.call_count == 1

    manager.retrials = set()
    assert {333} == await manager.scheduled()
    assert storage.get_tasks_queued.call_count == 2

    with pytest.raises(RuntimeError) as e:
        await manager.scheduled()
    assert "RuntimeError: coroutine raised StopIteration" in str(e)


@pytest.mark.asyncio
async def test_manager_process(factory: Factory):
    manager = Manager(name="name", storage=mock.Mock())
    storage = mock.Mock()
    storage.add_tasks_queued = mock.Mock()
    storage.add_info_items_processed = mock.Mock()
    storage.add_tasks_failed = mock.Mock()
    manager.storage = storage
    manager.event.is_set = mock.Mock(side_effect=[False])
    manager.event.set = mock.Mock()

    items = [factory.obj.product.create(), factory.obj.product.create()]
    tasks = {Task(url="url1"), Task(url="url2")}
    task = Task(url="url")
    result = Result(status=constants.status.OK, task=task, tasks=tasks, items=items)

    # test set event
    await manager.process(result=result)
    assert manager.iterations == 1
    assert manager.retrials == set()
    assert storage.add_tasks_queued.call_count == 1
    assert storage.add_info_items_processed.call_count == 1
    assert storage.add_tasks_failed.call_count == 0
    assert manager.event.is_set.call_count == 1
    assert manager.event.set.call_count == 1

    # test not set event
    manager.event.is_set = mock.Mock(side_effect=[True])
    await manager.process(result=result)
    assert manager.iterations == 2
    assert manager.retrials == set()
    assert storage.add_tasks_queued.call_count == 2
    assert storage.add_info_items_processed.call_count == 2
    assert storage.add_tasks_failed.call_count == 0
    assert manager.event.is_set.call_count == 1
    assert manager.event.set.call_count == 1


@pytest.mark.asyncio
async def test_manager_process_retrial(factory: Factory):
    manager = Manager(name="name", storage=mock.Mock())
    items = [factory.obj.product.create(), factory.obj.product.create()]
    tasks = {Task(url="url1"), Task(url="url2")}
    task = Task(url="url")
    result = Result(status=constants.status.RETRIAL, task=task, tasks=tasks, items=items)

    with factory.settings as s:
        s.set(dict(PAUSE_TIMEOUT=0))
        for i in range(1, settings.CONN_MAX_RETRIES + 1):
            if i == settings.CONN_MAX_RETRIES:
                with pytest.raises(exceptions.OkamiTerminationException) as e:
                    await manager.process(result=result)
                assert manager.iterations == i
                assert manager.retrials == {task}
                assert "CONN_MAX_RETRIES Reached. Terminating!" in str(e)
            else:
                await manager.process(result=result)
                assert manager.iterations == i
                assert manager.retrials == {task}


@pytest.mark.asyncio
async def test_manager_process_failed(factory: Factory):
    manager = Manager(name="name", storage=mock.Mock())
    storage = mock.Mock()
    storage.add_tasks_failed = mock.Mock()
    manager.storage = storage

    items = [factory.obj.product.create(), factory.obj.product.create()]
    tasks = {Task(url="url1"), Task(url="url2")}
    task = Task(url="url")
    result = Result(status=constants.status.FAILED, task=task, tasks=tasks, items=items)

    for i in range(1, settings.REQUEST_MAX_FAILED + 1):
        if i == settings.REQUEST_MAX_FAILED:
            storage.get_tasks_failed = mock.Mock(side_effect=[list(range(settings.REQUEST_MAX_FAILED))])
            with pytest.raises(exceptions.OkamiTerminationException) as e:
                await manager.process(result=result)
            assert manager.iterations == i
            assert manager.retrials == set()
            assert storage.add_tasks_failed.call_count == i
            assert storage.get_tasks_failed.call_count == 1
            assert "REQUEST_MAX_FAILED Reached. Terminating!" in str(e)
        else:
            storage.get_tasks_failed = mock.Mock(side_effect=[[1, 2, 3]])
            await manager.process(result=result)
            assert manager.iterations == i
            assert manager.retrials == set()
            assert storage.add_tasks_failed.call_count == i
            assert storage.get_tasks_failed.call_count == 1


@pytest.mark.asyncio
async def test_manager_stop():
    manager = Manager(name="name", storage=mock.Mock())
    assert manager.terminate is False
    assert await manager.stop() is True
    assert manager.terminate is True


def test_middlewares___init__(factory: Factory):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    middlewares = Middlewares(controller=controller)
    assert isinstance(middlewares.http, HttpMiddleware)
    assert isinstance(middlewares.spider, SpiderMiddleware)
    assert middlewares.http.controller is controller
    assert middlewares.spider.controller is controller


@pytest.mark.asyncio
async def test_middlewares_initialise(factory: Factory, coro):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    middlewares = Middlewares(controller=controller)
    middlewares.http.initialise = mock.Mock(side_effect=coro(mock.Mock()))
    middlewares.spider.initialise = mock.Mock(side_effect=coro(mock.Mock()))
    await middlewares.initialise()
    assert middlewares.http.initialise.call_count == 1
    assert middlewares.spider.initialise.call_count == 1


@pytest.mark.asyncio
async def test_middlewares_finalise(factory: Factory, coro):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    middlewares = Middlewares(controller=controller)
    middlewares.http.finalise = mock.Mock(side_effect=coro(mock.Mock()))
    middlewares.spider.finalise = mock.Mock(side_effect=coro(mock.Mock()))
    await middlewares.finalise()
    assert middlewares.http.finalise.call_count == 1
    assert middlewares.spider.finalise.call_count == 1


def test_middleware___init__(factory: Factory):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    middleware = Middleware(controller=controller)
    assert middleware.controller is controller
    assert middleware.sources == []
    assert middleware.cached == []


@pytest.mark.asyncio
async def test_middleware_middlewares(factory: Factory):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    middleware = Middleware(controller=controller)
    assert middleware.controller is controller
    assert middleware.cached == []
    assert middleware.middlewares == []
    assert middleware.cached == []

    sources = settings.BASE_HTTP_MIDDLEWARE + settings.BASE_HTTP_MIDDLEWARE
    assert len(sources) > 1
    middleware.sources = sources
    assert len(middleware.middlewares) == len(sources)
    assert len(middleware.cached) == len(sources)
    assert len(middleware.middlewares) == len(sources)
    assert len(middleware.cached) == len(sources)


@pytest.mark.asyncio
async def test_middleware_initialise():
    middleware = Middleware(controller=None)
    with pytest.raises(NotImplementedError):
        await middleware.initialise()


@pytest.mark.asyncio
async def test_middleware_before():
    middleware = Middleware(controller=None)
    with pytest.raises(NotImplementedError):
        await middleware.before()


@pytest.mark.asyncio
async def test_middleware_after():
    middleware = Middleware(controller=None)
    with pytest.raises(NotImplementedError):
        await middleware.after()


@pytest.mark.asyncio
async def test_middleware_finalise():
    middleware = Middleware(controller=None)
    with pytest.raises(NotImplementedError):
        await middleware.finalise()


def test_http_middleware__init__(factory: Factory):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    middleware = HttpMiddleware(controller=controller)
    sources = settings.BASE_HTTP_MIDDLEWARE + settings.HTTP_MIDDLEWARE
    assert len(sources) > 0
    assert middleware.sources == sources


@pytest.mark.asyncio
async def test_http_middleware_initialise(factory: Factory, coro):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    middleware = HttpMiddleware(controller=controller)

    assert middleware.sources == settings.BASE_HTTP_MIDDLEWARE + settings.HTTP_MIDDLEWARE
    assert len(middleware.sources)

    for m in middleware.middlewares:
        m.initialise = mock.Mock(side_effect=coro(mock.Mock()))

    with mock.patch("okami.engine.signals.http_middleware_initialised.send", side_effect=coro(mock.Mock())) as signal:
        assert await middleware.initialise() is None
        for m in middleware.middlewares:
            assert m.initialise.call_count == 1
            assert m.initialise.call_args == []
        assert signal.call_count == 2
        for m in middleware.middlewares:
            assert mock.call(sender=m) in signal.call_args_list

    # test exception
    for m in middleware.middlewares:
        m.initialise = mock.Mock(side_effect=coro(mock.Mock(side_effect=Exception)))
    with pytest.raises(exceptions.HttpMiddlewareException) as e:
        await middleware.initialise()
    assert "okami.exceptions.HttpMiddlewareException" in str(e)


@pytest.mark.asyncio
async def test_http_middleware_before(factory: Factory, coro):
    request = Request(url="url")
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    middleware = HttpMiddleware(controller=controller)

    assert middleware.sources == settings.BASE_HTTP_MIDDLEWARE + settings.HTTP_MIDDLEWARE
    assert len(middleware.sources)

    for m in middleware.middlewares:
        m.before = mock.Mock(side_effect=coro(mock.Mock(side_effect=[request])))

    with mock.patch("okami.engine.signals.http_middleware_started.send", side_effect=coro(mock.Mock())) as signal:
        assert await middleware.before(request=request) is request
        for m in middleware.middlewares:
            assert m.before.call_count == 1
            assert m.before.call_args == mock.call(request=request)
        assert signal.call_count == 2
        for m in middleware.middlewares:
            assert mock.call(sender=m, request=request) in signal.call_args_list

    # test exception
    for m in middleware.middlewares:
        m.before = mock.Mock(side_effect=coro(mock.Mock(side_effect=Exception)))
    with pytest.raises(exceptions.HttpMiddlewareException) as e:
        await middleware.before(request=request)
    assert "okami.exceptions.HttpMiddlewareException" in str(e)

    # test not implemented error
    for m in middleware.middlewares:
        m.before = mock.Mock(side_effect=coro(mock.Mock(side_effect=NotImplementedError)))
    assert await middleware.before(request=request) is request


@pytest.mark.asyncio
async def test_http_middleware_after(factory: Factory, coro):
    response = Response(
        url="url",
        version="version",
        status=constants.status.HTTP_501,
        reason="reason",
        headers=dict(a=1),
        text="<html></html>",
    )
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    middleware = HttpMiddleware(controller=controller)

    assert middleware.sources == settings.BASE_HTTP_MIDDLEWARE + settings.HTTP_MIDDLEWARE
    assert len(middleware.sources)

    for m in middleware.middlewares:
        m.after = mock.Mock(side_effect=coro(mock.Mock(side_effect=[response])))

    with mock.patch("okami.engine.signals.http_middleware_finished.send", side_effect=coro(mock.Mock())) as signal:
        assert await middleware.after(response=response) is response
        for m in middleware.middlewares:
            assert m.after.call_count == 1
            assert m.after.call_args == mock.call(response=response)
        assert signal.call_count == 2
        for m in middleware.middlewares:
            assert mock.call(sender=m, response=response) in signal.call_args_list

    # test exception
    for m in middleware.middlewares:
        m.after = mock.Mock(side_effect=coro(mock.Mock(side_effect=Exception)))
    with pytest.raises(exceptions.HttpMiddlewareException) as e:
        await middleware.after(response=response)
    assert "okami.exceptions.HttpMiddlewareException" in str(e)

    # test not implemented error
    for m in middleware.middlewares:
        m.after = mock.Mock(side_effect=coro(mock.Mock(side_effect=NotImplementedError)))
    assert await middleware.after(response=response) is response


@pytest.mark.asyncio
async def test_http_middleware_finalise(factory: Factory, coro):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    middleware = HttpMiddleware(controller=controller)

    assert middleware.sources == settings.BASE_HTTP_MIDDLEWARE + settings.HTTP_MIDDLEWARE
    assert len(middleware.sources)

    for m in middleware.middlewares:
        m.finalise = mock.Mock(side_effect=coro(mock.Mock()))

    with mock.patch("okami.engine.signals.http_middleware_finalised.send", side_effect=coro(mock.Mock())) as signal:
        assert await middleware.finalise() is None
        for m in middleware.middlewares:
            assert m.finalise.call_count == 1
            assert m.finalise.call_args == []
        assert signal.call_count == 2
        for m in middleware.middlewares:
            assert mock.call(sender=m) in signal.call_args_list

    # test exception
    for m in middleware.middlewares:
        m.finalise = mock.Mock(side_effect=coro(mock.Mock(side_effect=Exception)))
    with pytest.raises(exceptions.HttpMiddlewareException) as e:
        await middleware.finalise()
    assert "okami.exceptions.HttpMiddlewareException" in str(e)


def test_spider_middleware__init__(factory: Factory):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    middleware = SpiderMiddleware(controller=controller)
    sources = settings.BASE_SPIDER_MIDDLEWARE + settings.SPIDER_MIDDLEWARE
    assert len(sources) > 0
    assert middleware.sources == sources


@pytest.mark.asyncio
async def test_spider_middleware_initialise(factory: Factory, coro):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    middleware = SpiderMiddleware(controller=controller)

    assert middleware.sources == settings.BASE_SPIDER_MIDDLEWARE + settings.SPIDER_MIDDLEWARE
    assert len(middleware.sources)

    for m in middleware.middlewares:
        m.initialise = mock.Mock(side_effect=coro(mock.Mock()))

    with mock.patch("okami.engine.signals.spider_middleware_initialised.send", side_effect=coro(mock.Mock())) as signal:
        assert await middleware.initialise() is None
        for m in middleware.middlewares:
            assert m.initialise.call_count == 1
            assert m.initialise.call_args == []
        assert signal.call_count == 2
        for m in middleware.middlewares:
            assert mock.call(sender=m) in signal.call_args_list

    # test exception
    for m in middleware.middlewares:
        m.initialise = mock.Mock(side_effect=coro(mock.Mock(side_effect=Exception)))
    with pytest.raises(exceptions.SpiderMiddlewareException) as e:
        await middleware.initialise()
    assert "okami.exceptions.SpiderMiddlewareException" in str(e)


@pytest.mark.asyncio
async def test_spider_middleware_before(factory: Factory, coro):
    task = Task(url="url")
    response = Response(
        url="url",
        version="version",
        status=constants.status.HTTP_501,
        reason="reason",
        headers=dict(a=1),
        text="<html></html>",
    )
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    middleware = SpiderMiddleware(controller=controller)

    assert middleware.sources == settings.BASE_SPIDER_MIDDLEWARE + settings.SPIDER_MIDDLEWARE
    assert len(middleware.sources)

    for m in middleware.middlewares:
        m.before = mock.Mock(side_effect=coro(mock.Mock(side_effect=[response])))

    with mock.patch("okami.engine.signals.spider_middleware_started.send", side_effect=coro(mock.Mock())) as signal:
        assert await middleware.before(task=task, response=response) is response
        for m in middleware.middlewares:
            assert m.before.call_count == 1
            assert m.before.call_args == mock.call(task=task, response=response)
        assert signal.call_count == 2
        for m in middleware.middlewares:
            assert mock.call(sender=m, task=task, response=response) in signal.call_args_list

    # test exception
    for m in middleware.middlewares:
        m.before = mock.Mock(side_effect=coro(mock.Mock(side_effect=Exception)))
    with pytest.raises(exceptions.SpiderMiddlewareException) as e:
        await middleware.before(task=task, response=response)
    assert "okami.exceptions.SpiderMiddlewareException" in str(e)

    # test not implemented error
    for m in middleware.middlewares:
        m.before = mock.Mock(side_effect=coro(mock.Mock(side_effect=NotImplementedError)))
    assert await middleware.before(task=task, response=response) is response


@pytest.mark.asyncio
async def test_spider_middleware_after(factory: Factory, coro):
    task = Task(url="url")
    response = Response(
        url="url",
        version="version",
        status=constants.status.HTTP_501,
        reason="reason",
        headers=dict(a=1),
        text="<html></html>",
    )
    items = [factory.obj.product.create(), factory.obj.product.create()]
    tasks = {Task(url="url1"), Task(url="url2")}
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    middleware = SpiderMiddleware(controller=controller)

    assert middleware.sources == settings.BASE_SPIDER_MIDDLEWARE + settings.SPIDER_MIDDLEWARE
    assert len(middleware.sources)

    for m in middleware.middlewares:
        m.after = mock.Mock(side_effect=coro(mock.Mock(side_effect=[[tasks, items]])))

    with mock.patch("okami.engine.signals.spider_middleware_finished.send", side_effect=coro(mock.Mock())) as signal:
        assert await middleware.after(task=task, response=response, tasks=tasks, items=items) == (tasks, items)
        for m in middleware.middlewares:
            assert m.after.call_count == 1
            assert m.after.call_args == mock.call(task=task, response=response, tasks=tasks, items=items)
        assert signal.call_count == 2
        for m in middleware.middlewares:
            assert mock.call(sender=m, task=task, response=response, tasks=tasks, items=items) in signal.call_args_list

    # test exception
    for m in middleware.middlewares:
        m.after = mock.Mock(side_effect=coro(mock.Mock(side_effect=Exception)))
    with pytest.raises(exceptions.SpiderMiddlewareException) as e:
        await middleware.after(task=task, response=response, tasks=tasks, items=items)
    assert "okami.exceptions.SpiderMiddlewareException" in str(e)

    # test not implemented error
    for m in middleware.middlewares:
        m.after = mock.Mock(side_effect=coro(mock.Mock(side_effect=NotImplementedError)))
    assert await middleware.after(task=task, response=response, tasks=tasks, items=items) == (tasks, items)


@pytest.mark.asyncio
async def test_spider_middleware_finalise(factory: Factory, coro):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    middleware = SpiderMiddleware(controller=controller)

    assert middleware.sources == settings.BASE_SPIDER_MIDDLEWARE + settings.SPIDER_MIDDLEWARE
    assert len(middleware.sources)

    for m in middleware.middlewares:
        m.finalise = mock.Mock(side_effect=coro(mock.Mock()))

    with mock.patch("okami.engine.signals.spider_middleware_finalised.send", side_effect=coro(mock.Mock())) as signal:
        assert await middleware.finalise() is None
        for m in middleware.middlewares:
            assert m.finalise.call_count == 1
            assert m.finalise.call_args == []
        assert signal.call_count == 2
        for m in middleware.middlewares:
            assert mock.call(sender=m) in signal.call_args_list

    # test exception
    for m in middleware.middlewares:
        m.finalise = mock.Mock(side_effect=coro(mock.Mock(side_effect=Exception)))
    with pytest.raises(exceptions.SpiderMiddlewareException) as e:
        await middleware.finalise()
    assert "okami.exceptions.SpiderMiddlewareException" in str(e)


def test_pipelines___init__(factory: Factory):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    pipelines = Pipelines(controller=controller)
    assert isinstance(pipelines.startup, StartupPipeline)
    assert isinstance(pipelines.items, ItemsPipeline)
    assert isinstance(pipelines.tasks, TasksPipeline)
    assert pipelines.startup.controller is controller
    assert pipelines.items.controller is controller
    assert pipelines.tasks.controller is controller


@pytest.mark.asyncio
async def test_pipelines_initialise(factory: Factory, coro):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    pipelines = Pipelines(controller=controller)
    pipelines.startup.initialise = mock.Mock(side_effect=coro(mock.Mock()))
    pipelines.items.initialise = mock.Mock(side_effect=coro(mock.Mock()))
    pipelines.tasks.initialise = mock.Mock(side_effect=coro(mock.Mock()))
    await pipelines.initialise()
    assert pipelines.startup.initialise.call_count == 1
    assert pipelines.items.initialise.call_count == 1
    assert pipelines.tasks.initialise.call_count == 1


@pytest.mark.asyncio
async def test_pipelines_finalise(factory: Factory, coro):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    pipelines = Pipelines(controller=controller)
    pipelines.startup.finalise = mock.Mock(side_effect=coro(mock.Mock()))
    pipelines.items.finalise = mock.Mock(side_effect=coro(mock.Mock()))
    pipelines.tasks.finalise = mock.Mock(side_effect=coro(mock.Mock()))
    await pipelines.finalise()
    assert pipelines.startup.finalise.call_count == 1
    assert pipelines.items.finalise.call_count == 1
    assert pipelines.tasks.finalise.call_count == 1


def test_pipeline___init__(factory: Factory):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    pipeline = Pipeline(controller=controller)
    assert pipeline.controller is controller
    assert pipeline.sources == []
    assert pipeline.cached == []


@pytest.mark.asyncio
async def test_pipeline_pipelines(factory: Factory):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    pipeline = Pipeline(controller=controller)
    assert pipeline.controller is controller
    assert pipeline.cached == []
    assert pipeline.pipelines == []
    assert pipeline.cached == []

    sources = settings.BASE_STARTUP_PIPELINE + settings.STARTUP_PIPELINE
    assert len(sources) > 1
    pipeline.sources = sources
    assert len(pipeline.pipelines) == len(sources)
    assert len(pipeline.cached) == len(sources)
    assert len(pipeline.pipelines) == len(sources)
    assert len(pipeline.cached) == len(sources)


@pytest.mark.asyncio
async def test_pipeline_initialise():
    pipeline = Pipeline(controller=None)
    with pytest.raises(NotImplementedError):
        await pipeline.initialise()


@pytest.mark.asyncio
async def test_pipeline_process():
    pipeline = Pipeline(controller=None)
    with pytest.raises(NotImplementedError):
        await pipeline.process(something=mock.Mock())


@pytest.mark.asyncio
async def test_pipeline_finalise():
    pipeline = Pipeline(controller=None)
    with pytest.raises(NotImplementedError):
        await pipeline.finalise()


def test_startup_pipeline___init__(factory: Factory):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    pipeline = StartupPipeline(controller=controller)
    sources = settings.BASE_STARTUP_PIPELINE + settings.STARTUP_PIPELINE
    assert len(sources) > 0
    assert pipeline.sources == sources


@pytest.mark.asyncio
async def test_startup_pipeline_initialise(factory: Factory, coro):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    pipeline = StartupPipeline(controller=controller)

    assert pipeline.sources == settings.BASE_STARTUP_PIPELINE + settings.STARTUP_PIPELINE
    assert len(pipeline.sources)

    for p in pipeline.pipelines:
        p.initialise = mock.Mock(side_effect=coro(mock.Mock()))

    with mock.patch("okami.engine.signals.startup_pipeline_initialised.send", side_effect=coro(mock.Mock())) as signal:
        assert await pipeline.initialise() is None
        for p in pipeline.pipelines:
            assert p.initialise.call_count == 1
            assert p.initialise.call_args == []
        assert signal.call_count == 2
        for p in pipeline.pipelines:
            assert mock.call(sender=p) in signal.call_args_list

    # test exception
    for p in pipeline.pipelines:
        p.initialise = mock.Mock(side_effect=coro(mock.Mock(side_effect=Exception)))
    with pytest.raises(exceptions.StartupPipelineException) as e:
        await pipeline.initialise()
    assert "okami.exceptions.StartupPipelineException" in str(e)


@pytest.mark.asyncio
async def test_startup_pipeline_process(factory: Factory, coro):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    pipeline = StartupPipeline(controller=controller)

    assert pipeline.sources == settings.BASE_STARTUP_PIPELINE + settings.STARTUP_PIPELINE
    assert len(pipeline.sources)

    for p in pipeline.pipelines:
        p.process = mock.Mock(side_effect=coro(mock.Mock(side_effect=[spider])))

    s1v = dict(target="okami.engine.signals.startup_pipeline_started.send", side_effect=coro(mock.Mock()))
    s2v = dict(target="okami.engine.signals.startup_pipeline_finished.send", side_effect=coro(mock.Mock()))
    with mock.patch(**s1v) as s1, mock.patch(**s2v) as s2:
        assert await pipeline.process(spider=spider) is spider
        for p in pipeline.pipelines:
            assert p.process.call_count == 1
            assert p.process.call_args == mock.call(spider=spider)
        assert s1.call_count == 2
        assert s2.call_count == 2
        for p in pipeline.pipelines:
            assert mock.call(sender=p, spider=spider) in s1.call_args_list
            assert mock.call(sender=p, spider=spider) in s2.call_args_list

    # test exception
    for p in pipeline.pipelines:
        p.process = mock.Mock(side_effect=coro(mock.Mock(side_effect=Exception)))
    with pytest.raises(exceptions.StartupPipelineException) as e:
        await pipeline.process(spider=spider)
    assert "okami.exceptions.StartupPipelineException" in str(e)

    # test not implemented error
    for p in pipeline.pipelines:
        p.process = mock.Mock(side_effect=coro(mock.Mock(side_effect=NotImplementedError)))
    assert await pipeline.process(spider=spider) is spider


@pytest.mark.asyncio
async def test_startup_pipeline_finalise(factory: Factory, coro):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    pipeline = StartupPipeline(controller=controller)

    assert pipeline.sources == settings.BASE_STARTUP_PIPELINE + settings.STARTUP_PIPELINE
    assert len(pipeline.sources)

    for p in pipeline.pipelines:
        p.finalise = mock.Mock(side_effect=coro(mock.Mock()))

    with mock.patch("okami.engine.signals.startup_pipeline_finalised.send", side_effect=coro(mock.Mock())) as signal:
        assert await pipeline.finalise() is None
        for p in pipeline.pipelines:
            assert p.finalise.call_count == 1
            assert p.finalise.call_args == []
        assert signal.call_count == 2
        for p in pipeline.pipelines:
            assert mock.call(sender=p) in signal.call_args_list

    # test exception
    for p in pipeline.pipelines:
        p.finalise = mock.Mock(side_effect=coro(mock.Mock(side_effect=Exception)))
    with pytest.raises(exceptions.StartupPipelineException) as e:
        await pipeline.finalise()
    assert "okami.exceptions.StartupPipelineException" in str(e)


def test_items_pipeline___init__(factory: Factory):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    pipeline = ItemsPipeline(controller=controller)
    sources = settings.BASE_ITEMS_PIPELINE + settings.ITEMS_PIPELINE
    assert len(sources) > 0
    assert pipeline.sources == sources


@pytest.mark.asyncio
async def test_items_pipeline_initialise(factory: Factory, coro):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    pipeline = ItemsPipeline(controller=controller)

    assert pipeline.sources == settings.BASE_ITEMS_PIPELINE + settings.ITEMS_PIPELINE
    assert len(pipeline.sources)

    for p in pipeline.pipelines:
        p.initialise = mock.Mock(side_effect=coro(mock.Mock()))

    with mock.patch("okami.engine.signals.items_pipeline_initialised.send", side_effect=coro(mock.Mock())) as signal:
        assert await pipeline.initialise() is None
        for p in pipeline.pipelines:
            assert p.initialise.call_count == 1
            assert p.initialise.call_args == []
        assert signal.call_count == 3
        for p in pipeline.pipelines:
            assert mock.call(sender=p) in signal.call_args_list

    # test exception
    for p in pipeline.pipelines:
        p.initialise = mock.Mock(side_effect=coro(mock.Mock(side_effect=Exception)))
    with pytest.raises(exceptions.ItemsPipelineException) as e:
        await pipeline.initialise()
    assert "okami.exceptions.ItemsPipelineException" in str(e)


@pytest.mark.asyncio
async def test_items_pipeline_process(factory: Factory, coro):
    items = [factory.obj.product.create(), factory.obj.product.create()]
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    pipeline = ItemsPipeline(controller=controller)

    assert pipeline.sources == settings.BASE_ITEMS_PIPELINE + settings.ITEMS_PIPELINE
    assert len(pipeline.sources)

    for p in pipeline.pipelines:
        p.process = mock.Mock(side_effect=coro(mock.Mock(side_effect=[items])))

    s1v = dict(target="okami.engine.signals.items_pipeline_started.send", side_effect=coro(mock.Mock()))
    s2v = dict(target="okami.engine.signals.items_pipeline_finished.send", side_effect=coro(mock.Mock()))
    with mock.patch(**s1v) as s1, mock.patch(**s2v) as s2:
        assert await pipeline.process(items=items) is items
        for p in pipeline.pipelines:
            assert p.process.call_count == 1
            assert p.process.call_args == mock.call(items=items)
        assert s1.call_count == 3
        assert s2.call_count == 3
        for p in pipeline.pipelines:
            assert mock.call(sender=p, items=items) in s1.call_args_list
            assert mock.call(sender=p, items=items) in s2.call_args_list

    # test exception
    for p in pipeline.pipelines:
        p.process = mock.Mock(side_effect=coro(mock.Mock(side_effect=Exception)))
    with pytest.raises(exceptions.ItemsPipelineException) as e:
        await pipeline.process(items=items)
    assert "okami.exceptions.ItemsPipelineException" in str(e)

    # test not implemented error
    for p in pipeline.pipelines:
        p.process = mock.Mock(side_effect=coro(mock.Mock(side_effect=NotImplementedError)))
    assert await pipeline.process(items=items) is items


@pytest.mark.asyncio
async def test_items_pipeline_finalise(factory: Factory, coro):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    pipeline = ItemsPipeline(controller=controller)

    assert pipeline.sources == settings.BASE_ITEMS_PIPELINE + settings.ITEMS_PIPELINE
    assert len(pipeline.sources)

    for p in pipeline.pipelines:
        p.finalise = mock.Mock(side_effect=coro(mock.Mock()))

    with mock.patch("okami.engine.signals.items_pipeline_finalised.send", side_effect=coro(mock.Mock())) as signal:
        assert await pipeline.finalise() is None
        for p in pipeline.pipelines:
            assert p.finalise.call_count == 1
            assert p.finalise.call_args == []
        assert signal.call_count == 3
        for p in pipeline.pipelines:
            assert mock.call(sender=p) in signal.call_args_list

    # test exception
    for p in pipeline.pipelines:
        p.finalise = mock.Mock(side_effect=coro(mock.Mock(side_effect=Exception)))
    with pytest.raises(exceptions.ItemsPipelineException) as e:
        await pipeline.finalise()
    assert "okami.exceptions.ItemsPipelineException" in str(e)


def test_tasks_pipeline___init__(factory: Factory):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    pipeline = TasksPipeline(controller=controller)
    sources = settings.BASE_TASKS_PIPELINE + settings.TASKS_PIPELINE
    assert len(sources) > 0
    assert pipeline.sources == sources


@pytest.mark.asyncio
async def test_tasks_pipeline_initialise(factory: Factory, coro):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    pipeline = TasksPipeline(controller=controller)

    assert pipeline.sources == settings.BASE_TASKS_PIPELINE + settings.TASKS_PIPELINE
    assert len(pipeline.sources)

    for p in pipeline.pipelines:
        p.initialise = mock.Mock(side_effect=coro(mock.Mock()))

    with mock.patch("okami.engine.signals.tasks_pipeline_initialised.send", side_effect=coro(mock.Mock())) as signal:
        assert await pipeline.initialise() is None
        for p in pipeline.pipelines:
            assert p.initialise.call_count == 1
            assert p.initialise.call_args == []
        assert signal.call_count == 1
        for p in pipeline.pipelines:
            assert mock.call(sender=p) in signal.call_args_list

    # test exception
    for p in pipeline.pipelines:
        p.initialise = mock.Mock(side_effect=coro(mock.Mock(side_effect=Exception)))
    with pytest.raises(exceptions.TasksPipelineException) as e:
        await pipeline.initialise()
    assert "okami.exceptions.TasksPipelineException" in str(e)


@pytest.mark.asyncio
async def test_tasks_pipeline_process(factory: Factory, coro):
    tasks = {Task(url="url1"), Task(url="url2")}
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    pipeline = TasksPipeline(controller=controller)

    assert pipeline.sources == settings.BASE_TASKS_PIPELINE + settings.TASKS_PIPELINE
    assert len(pipeline.sources)

    for p in pipeline.pipelines:
        p.process = mock.Mock(side_effect=coro(mock.Mock(side_effect=[tasks])))

    s1v = dict(target="okami.engine.signals.tasks_pipeline_started.send", side_effect=coro(mock.Mock()))
    s2v = dict(target="okami.engine.signals.tasks_pipeline_finished.send", side_effect=coro(mock.Mock()))
    with mock.patch(**s1v) as s1, mock.patch(**s2v) as s2:
        assert await pipeline.process(tasks=tasks) is tasks
        for p in pipeline.pipelines:
            assert p.process.call_count == 1
            assert p.process.call_args == mock.call(tasks=tasks)
        assert s1.call_count == 1
        assert s2.call_count == 1
        for p in pipeline.pipelines:
            assert mock.call(sender=p, tasks=tasks) in s1.call_args_list
            assert mock.call(sender=p, tasks=tasks) in s2.call_args_list

    # test exception
    for p in pipeline.pipelines:
        p.process = mock.Mock(side_effect=coro(mock.Mock(side_effect=Exception)))
    with pytest.raises(exceptions.TasksPipelineException) as e:
        await pipeline.process(tasks=tasks)
    assert "okami.exceptions.TasksPipelineException" in str(e)

    # test not implemented error
    for p in pipeline.pipelines:
        p.process = mock.Mock(side_effect=coro(mock.Mock(side_effect=NotImplementedError)))
    assert await pipeline.process(tasks=tasks) is tasks


@pytest.mark.asyncio
async def test_tasks_pipeline_finalise(factory: Factory, coro):
    spider = factory.obj.spider.create()
    controller = Controller(spider=spider)
    pipeline = TasksPipeline(controller=controller)

    assert pipeline.sources == settings.BASE_TASKS_PIPELINE + settings.TASKS_PIPELINE
    assert len(pipeline.sources)

    for p in pipeline.pipelines:
        p.finalise = mock.Mock(side_effect=coro(mock.Mock()))

    with mock.patch("okami.engine.signals.tasks_pipeline_finalised.send", side_effect=coro(mock.Mock())) as signal:
        assert await pipeline.finalise() is None
        for p in pipeline.pipelines:
            assert p.finalise.call_count == 1
            assert p.finalise.call_args == []
        assert signal.call_count == 1
        for p in pipeline.pipelines:
            assert mock.call(sender=p) in signal.call_args_list

    # test exception
    for p in pipeline.pipelines:
        p.finalise = mock.Mock(side_effect=coro(mock.Mock(side_effect=Exception)))
    with pytest.raises(exceptions.TasksPipelineException) as e:
        await pipeline.finalise()
    assert "okami.exceptions.TasksPipelineException" in str(e)

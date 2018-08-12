import hashlib
import json
import os
import time
from unittest import mock

import aiohttp
import pytest

import okami
from okami import constants, Request, Response, settings, Task
from okami.engine import Controller
from okami.middleware import Delta, DeltaSqlite, Headers, Logger, Middleware, Session
from tests.factory import Factory


def test_middleware___init__():
    controller = object()
    middleware = Middleware(controller=controller)
    assert middleware.controller is controller


@pytest.mark.asyncio
async def test_middleware_initialise():
    middleware = Middleware(controller=object())
    assert await middleware.initialise() is None


@pytest.mark.asyncio
async def test_middleware_before():
    middleware = Middleware(controller=object())
    with pytest.raises(NotImplementedError):
        await middleware.before(something=mock.Mock())


@pytest.mark.asyncio
async def test_middleware_after():
    middleware = Middleware(controller=object())
    with pytest.raises(NotImplementedError):
        await middleware.after(something=mock.Mock())


@pytest.mark.asyncio
async def test_middleware_finalise():
    middleware = Middleware(controller=object())
    assert await middleware.finalise() is None


def test_delta___init__():
    delta = Delta(controller=object())
    assert delta.db is None
    assert delta.key_added == "delta/added"
    assert delta.key_skipped == "delta/skipped"


@pytest.mark.asyncio
async def test_delta_initialise(factory: Factory, tmpdir):
    controller = Controller(spider=factory.obj.spider.create())
    delta = Delta(controller=controller)
    assert delta.db is None
    assert await delta.initialise() is None
    assert delta.db is None

    with factory.settings as s:
        s.set(dict(DELTA_ENABLED=True, DELTA_PATH=str(tmpdir)))
        delta = Delta(controller=controller)
        await delta.initialise()
        assert delta.db is not None
        assert delta.filename == os.path.join(str(tmpdir), "{}.json".format(controller.spider.name))
        assert os.path.exists(delta.filename)


@pytest.mark.asyncio
async def test_delta_before(factory: Factory, tmpdir):
    response = Response(
        url="url",
        version="version",
        status=constants.status.HTTP_501,
        reason="reason",
        headers=dict(a=1),
        text="<html></html>",
    )
    controller = Controller(spider=factory.obj.spider.create())
    with factory.settings as s:
        s.set(dict(DELTA_ENABLED=True, DELTA_PATH=str(tmpdir)))
        delta = Delta(controller=controller)
        with pytest.raises(NotImplementedError):
            assert response is await delta.before(task=mock.Mock(), response=response)
        assert response is response


@pytest.mark.freeze_time("2016-12-23 00:00:00")
@pytest.mark.asyncio
async def test_delta_after(factory: Factory, tmpdir):
    controller = Controller(spider=factory.obj.spider.create())
    controller.stats.incr = mock.Mock()

    task = Task(url="url")
    tasks = {Task(url="url1"), Task(url="url2")}
    items = [factory.obj.product.create(), factory.obj.product.create()]

    with factory.settings as s:
        s.set(dict(DELTA_ENABLED=True, DELTA_PATH=str(tmpdir)))
        delta = Delta(controller=controller)
        delta.db = None
        assert (tasks, items) == await delta.after(
            task=task, response=object(), tasks=tasks, items=items
        )

    with factory.settings as s:
        s.set(dict(DELTA_ENABLED=True, DELTA_PATH=str(tmpdir)))
        delta = Delta(controller=controller)
        assert await delta.initialise() is None
        assert (tasks, items) == await delta.after(
            task=task, response=object(), tasks=tasks, items=items
        )
        assert controller.stats.incr.call_count == 1
        assert delta.db == {hashlib.sha1(task.url.encode()).hexdigest(): str(time.time())}

        assert (tasks, items) == await delta.after(
            task=task, response=object(), tasks=tasks, items=items
        )
        assert controller.stats.incr.call_count == 2
        assert delta.db == {hashlib.sha1(task.url.encode()).hexdigest(): str(time.time())}

        t1 = Task(url="url1")
        assert ({Task(url="url2")}, items) == await delta.after(
            task=t1, response=object(), tasks={Task(url="url2")}, items=items
        )
        assert controller.stats.incr.call_count == 3
        assert delta.db == {
            hashlib.sha1(t1.url.encode()).hexdigest(): str(time.time()),
            hashlib.sha1(task.url.encode()).hexdigest(): str(time.time()),
        }

        # task t1 should now exist in db
        assert ({Task(url="url2")}, items) == await delta.after(
            task=t1, response=object(), tasks={t1, Task(url="url2")}, items=items
        )
        assert controller.stats.incr.call_count == 5
        assert delta.db == {
            hashlib.sha1(t1.url.encode()).hexdigest(): str(time.time()),
            hashlib.sha1(task.url.encode()).hexdigest(): str(time.time()),
        }


@pytest.mark.freeze_time("2016-12-23 00:00:00")
@pytest.mark.asyncio
async def test_delta_finalise(factory: Factory, tmpdir):
    controller = Controller(spider=factory.obj.spider.create())
    task = Task(url="url")
    tasks = {Task(url="url1"), Task(url="url2")}
    items = [[factory.obj.product.create(), factory.obj.product.create()]]

    with factory.settings as s:
        s.set(dict(DELTA_ENABLED=True, DELTA_PATH=str(tmpdir)))
        delta = Delta(controller=controller)
        assert await delta.initialise() is None
        assert delta.db is not None
        assert delta.filename == os.path.join(str(tmpdir), "{}.json".format(controller.spider.name))
        assert (tasks, items) == await delta.after(
            task=task, response=object(), tasks=tasks, items=items
        )
        await delta.finalise()
        assert os.path.exists(delta.filename)
        assert json.load(open(delta.filename)) == {
            hashlib.sha1(task.url.encode()).hexdigest(): str(time.time()),
        }


def test_delta_sqlite___init__():
    delta = DeltaSqlite(controller=object())
    assert delta.db is None
    assert delta.key_added == "delta/added"
    assert delta.key_skipped == "delta/skipped"


@pytest.mark.asyncio
async def test_delta_sqlite_initialise(factory: Factory, tmpdir):
    controller = Controller(spider=factory.obj.spider.create())
    delta = DeltaSqlite(controller=controller)
    assert delta.db is None
    await delta.initialise()
    assert delta.db is None

    with factory.settings as s:
        s.set(dict(DELTA_ENABLED=True, DELTA_PATH=str(tmpdir)))
        delta = DeltaSqlite(controller=controller)
        assert await delta.initialise() is None
        assert delta.db is not None
        assert delta.db.conn is not None
        assert delta.db.filename == os.path.join(str(tmpdir), "{}.sqlite".format(controller.spider.name))
        assert os.path.exists(delta.filename)


@pytest.mark.asyncio
async def test_delta_sqlite_before(factory: Factory, tmpdir):
    response = object()
    with factory.settings as s:
        s.set(dict(DELTA_ENABLED=True, DELTA_PATH=str(tmpdir)))
        delta = DeltaSqlite(controller=object())
        with pytest.raises(NotImplementedError):
            assert response is await delta.before(task=mock.Mock(), response=response)
        assert response is response


@pytest.mark.freeze_time("2016-12-23 00:00:00")
@pytest.mark.asyncio
async def test_delta_sqlite_after(factory: Factory, tmpdir):
    controller = Controller(spider=factory.obj.spider.create())
    controller.stats.incr = mock.Mock()

    task = Task(url="url")
    tasks = {Task(url="url1"), Task(url="url2")}
    items = [[factory.obj.product.create(), factory.obj.product.create()]]

    with factory.settings as s:
        s.set(dict(DELTA_ENABLED=True, DELTA_PATH=str(tmpdir)))
        delta = DeltaSqlite(controller=controller)
        delta.db = None
        assert (tasks, items) == await delta.after(
            task=task, response=object(), tasks=tasks, items=items
        )

    with factory.settings as s:
        s.set(dict(DELTA_ENABLED=True, DELTA_PATH=str(tmpdir)))
        delta = DeltaSqlite(controller=controller)
        await delta.initialise()
        assert (tasks, items) == await delta.after(
            task=task, response=object(), tasks=tasks, items=items
        )
        assert controller.stats.incr.call_count == 1
        assert delta.db == {hashlib.sha1(task.url.encode()).hexdigest(): str(time.time())}

        assert (tasks, items) == await delta.after(
            task=task, response=object(), tasks=tasks, items=items
        )
        assert controller.stats.incr.call_count == 2
        assert delta.db == {hashlib.sha1(task.url.encode()).hexdigest(): str(time.time())}

        t1 = Task(url="url1")
        assert ({Task(url="url2")}, items) == await delta.after(
            task=t1, response=object(), tasks={Task(url="url2")}, items=items
        )
        assert controller.stats.incr.call_count == 3
        assert delta.db == {
            hashlib.sha1(t1.url.encode()).hexdigest(): str(time.time()),
            hashlib.sha1(task.url.encode()).hexdigest(): str(time.time()),
        }

        # task t1 should now exist in db
        assert ({Task(url="url2")}, items) == await delta.after(
            task=t1, response=object(), tasks={t1, Task(url="url2")}, items=items
        )
        assert controller.stats.incr.call_count == 5
        assert delta.db == {
            hashlib.sha1(t1.url.encode()).hexdigest(): str(time.time()),
            hashlib.sha1(task.url.encode()).hexdigest(): str(time.time()),
        }


@pytest.mark.asyncio
async def test_delta_sqlite_finalise(factory: Factory, tmpdir):
    controller = Controller(spider=factory.obj.spider.create())
    with factory.settings as s:
        s.set(dict(DELTA_ENABLED=True, DELTA_PATH=str(tmpdir)))
        delta = DeltaSqlite(controller=controller)
        assert await delta.initialise() is None
        assert delta.db is not None
        assert delta.db.conn is not None
        assert delta.db.filename == os.path.join(str(tmpdir), "{}.sqlite".format(controller.spider.name))
        await delta.finalise()
        assert os.path.exists(delta.filename)
        assert delta.db.conn is None


@pytest.mark.asyncio
async def test_logger_after(factory: Factory, capsys):
    controller = Controller(spider=factory.obj.spider.create())
    response = Response(
        url="url",
        version="version",
        status=constants.status.HTTP_501,
        reason="reason",
        headers=dict(a=1),
        text="<html></html>",
    )

    logger = Logger(controller=controller)
    assert await logger.after(response=response) is response
    captured = capsys.readouterr()
    for s in ["Okami", "test-spider", "delta=", "sleep=", "time=", "rps=", "i=", "0.00s"]:
        assert s in captured.out


@pytest.mark.asyncio
async def test_logger_finalise(factory: Factory, capsys):
    controller = Controller(spider=factory.obj.spider.create())
    logger = Logger(controller=controller)
    assert await logger.finalise() is None
    captured = capsys.readouterr()
    for s in [
        "storage/items_failed",
        "storage/items_processed",
        "storage/tasks_failed",
        "storage/tasks_processed",
        "storage/tasks_queued",
        "storage/times_running",
        "throttle/delta",
        "throttle/iterations",
        "throttle/rps",
        "throttle/sleep",
        "throttle/time",
    ]:
        assert s in captured.out


@pytest.mark.asyncio
async def test_headers_before(factory: Factory):
    request = Request(url="url", headers={})
    controller = Controller(spider=factory.obj.spider.create())
    headers = Headers(controller=controller)
    assert await headers.before(request=request) is request
    assert request.headers == {"User-Agent": "Okami/{}".format(okami.__version__)}


@pytest.mark.asyncio
async def test_session_before(factory: Factory):
    request = Request(url="url", headers={})
    controller = Controller(spider=factory.obj.spider.create())
    assert controller.session is None
    session = Session(controller=controller)
    assert await session.before(request=request) is request
    s1 = controller.session
    assert isinstance(s1, aiohttp.ClientSession)
    assert s1.connector._limit == settings.CONN_MAX_CONCURRENT_CONNECTIONS
    assert s1.connector._ssl == settings.CONN_VERIFY_SSL

    assert await session.before(request=request) is request
    s2 = controller.session
    assert s1 is s2
    assert isinstance(s2, aiohttp.ClientSession)
    assert s2.connector._limit == settings.CONN_MAX_CONCURRENT_CONNECTIONS
    assert s2.connector._ssl == settings.CONN_VERIFY_SSL

    controller.session._connector = None
    assert await session.before(request=request) is request
    s3 = controller.session
    assert s3 is not s1
    assert isinstance(s3, aiohttp.ClientSession)
    assert s3.connector._limit == settings.CONN_MAX_CONCURRENT_CONNECTIONS
    assert s3.connector._ssl == settings.CONN_VERIFY_SSL

    for s in [s2, s3]:
        await s.close()

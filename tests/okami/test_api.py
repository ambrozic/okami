import time
from collections import namedtuple
from unittest import mock

import aiohttp
import pytest
import yarl
from aiohttp import web

from okami import constants
from okami.api import Downloader, Item, Response, Result, Request, State, Stats, Task, Throttle
from okami.engine import Controller
from tests.factory import Factory


def test_downloader___init__():
    controller = object()
    downloader = Downloader(controller=controller)
    assert downloader.controller is controller


@pytest.mark.asyncio
async def test_downloader_process(factory: Factory, server):
    async with server(app=web.Application(), port=8888):
        controller = Controller(spider=factory.obj.spider.create())
        downloader = Downloader(controller=controller)
        request = Request(url="http://127.0.0.1:8888/")

        # session is none at this point
        with pytest.raises(AttributeError) as e:
            await downloader.process(request=request)
        assert "'NoneType' object has no attribute 'request'" in str(e)

        # create with session
        controller.session = aiohttp.ClientSession()
        response = await downloader.process(request=request)
        assert isinstance(response.url, yarl.URL)
        assert str(response.url) == request.url
        assert response.status == 404
        assert response.reason == "Not Found"
        assert "Content-Type" in response.headers
        assert "Content-Length" in response.headers
        assert response.text == "404: Not Found"

        await controller.session.close()


def test_item_to_dict():
    pytest.raises(NotImplementedError, Item().to_dict)


def test_request():
    request = Request(url="url")
    assert request.url == "url"
    assert request.headers == dict()

    request = Request(url="url", headers=dict(a=1))
    assert request.url == "url"
    assert request.headers == dict(a=1)


def test_response():
    response = Response(
        url="url",
        version="version",
        status=constants.status.HTTP_501,
        reason="reason",
        headers=dict(a=1),
        text="<html></html>",
    )
    assert response.url == "url"
    assert response.version == "version"
    assert response.status == constants.status.HTTP_501
    assert response.reason == "reason"
    assert response.headers == dict(a=1)
    assert response.text == "<html></html>"


def test_result():
    task = Task(url="url")
    tasks = {Task(url="url1"), Task(url="url2"), Task(url="url3")}
    items = {Item(), Item(), Item(), Item(), Item()}
    result = Result(status=constants.status.HTTP_501, task=task, tasks=tasks, items=items)
    assert result.status == constants.status.HTTP_501
    assert result.task is task
    assert result.tasks is tasks
    assert result.items is items


def test_state___init__():
    args = dict(sleep=1.23, max_rps=12.34)
    state = State(**args)
    assert state.iterations == 0
    assert state.sleep == args["sleep"]
    assert state.delta == args["sleep"]
    assert state.rps == 0.0
    assert state.max_rps == args["max_rps"]
    assert state.time_running == 0

    args = dict(sleep=1.23, max_rps=None)
    state = State(**args)
    assert state.iterations == 0
    assert state.sleep == 0.0001
    assert state.delta == args["sleep"]
    assert state.rps == 0.0
    assert state.max_rps == args["max_rps"]
    assert state.time_running == 0


def test_state_to_dict():
    args = dict(sleep=1.23, max_rps=12.34)
    state = State(**args)
    assert state.to_dict() == dict(
        iterations=0, sleep=args["sleep"], delta=args["sleep"], time=args["sleep"] * 2, rps=0.0
    )
    args = dict(sleep=1.23, max_rps=None)
    state = State(**args)
    assert state.to_dict() == dict(
        iterations=0, sleep=0.0001, delta=args["sleep"], time=args["sleep"] + 0.0001, rps=0.0
    )


def test_stats___init__():
    controller = object()
    stats = Stats(controller=controller)
    assert stats.controller is controller
    assert stats.data == dict()


def test_stats_collect():
    controller = mock.Mock(
        storage=mock.Mock(to_dict=lambda: dict(a=1, b=2)),
        throttle=mock.Mock(to_dict=lambda: dict(a=11, b=22)),
    )
    controller.xxxx()
    stats = Stats(controller=controller)
    assert stats.collect() == {"storage/a": 1, "storage/b": 2, "throttle/a": 11, "throttle/b": 22}
    stats.set("key", 123)
    assert stats.collect() == {"storage/a": 1, "storage/b": 2, "throttle/a": 11, "throttle/b": 22, "key": 123}
    assert stats.data == {"storage/a": 1, "storage/b": 2, "throttle/a": 11, "throttle/b": 22, "key": 123}


def test_stats_get():
    stats = Stats(controller=object())
    assert stats.get("key") is None
    assert stats.get("key", 12) == 12
    stats.set("key", 123)
    assert stats.get("key") == 123
    assert stats.data == dict(key=123)


def test_stats_set():
    stats = Stats(controller=object())
    assert stats.data == dict()
    stats.set("key", 123)
    assert stats.data == dict(key=123)
    stats.set("key", 123)
    assert stats.data == dict(key=123)
    stats.set("key", 1234)
    assert stats.data == dict(key=1234)
    stats.set("key1", 11)
    assert stats.data == dict(key=1234, key1=11)


def test_stats_decr():
    stats = Stats(controller=object())
    with pytest.raises(KeyError):
        stats.incr(key="key")
    stats.set(key="key", value=10)
    assert stats.data == dict(key=10)
    stats.incr(key="key")
    assert stats.data == dict(key=11)
    stats.incr(key="key", value=4)
    assert stats.data == dict(key=15)


def test_stats_incr():
    stats = Stats(controller=object())
    with pytest.raises(KeyError):
        stats.incr("key")
    stats.set("key", 10)
    assert stats.data == dict(key=10)
    stats.decr(key="key")
    assert stats.data == dict(key=9)
    stats.decr(key="key", value=4)
    assert stats.data == dict(key=5)


def test_task___init__():
    task = Task(url="url")
    assert task.url == "url"

    task = Task(url="url", data=1)
    assert task.url == "url"
    assert task.data == 1


def test_task___repr__():
    task = Task(url="url")
    assert str(task) == "<Task url=url>"

    task = Task(url="url", data=1)
    assert str(task) == "<Task url=url>"


def test_task___eq__():
    assert Task(url="url") == Task(url="url")
    assert Task(url="url", data=1) == Task(url="url", data=1)
    assert Task(url="url", data=dict(b=2, a=1)) == Task(url="url", data=dict(a=1, b=2))
    assert Task(url="url", data=[1, 2, 3]) == Task(url="url", data=[1, 2, 3])

    assert Task(url="url1", data=1) != Task(url="url2", data=1)
    assert Task(url="url", data=1) != Task(url="url", data=2)
    assert Task(url="url", data=[1, 2, 3]) != Task(url="url", data=[2, 1, 3])


def test_task___hash__():
    assert hash(Task(url="url")) == hash(("url", None))
    assert hash(Task(url="url")) != hash(("url"))
    assert hash(Task(url="url", data=1)) == hash(("url", 1))
    assert hash(Task(url="url", data=None)) == hash(("url", None))
    assert 2 == len({Task(url="url"), Task(url="url"), Task(url="url2")})
    assert 2 == len({Task(url="url", data=1), Task(url="url", data=1), Task(url="url", data=2)})


def test_task___ne__():
    assert Task(url="url1") != Task(url="url2")
    assert Task(url="url", data=1) != Task(url="url")
    assert Task(url="url", data=1) != Task(url="url", data=2)
    assert Task(url="url") != Task(url="url", data=2)

    assert Task(url=None) != "url"
    assert Task(url="url") != "url"

    Obj = namedtuple("Task", ["url", "data"])
    assert Task(url="url") != Obj(url="url", data=None)
    assert Task(url="url", data=1) != Obj(url="url", data=1)
    assert Task(url="url", data=1) != Obj(url="url", data=1)
    assert Task(url=None, data=1) != Obj(url=None, data=1)
    assert Task(url=None, data=None) != Obj(url=None, data=None)


def test_task_from_dict():
    args = dict(url="url", data=dict(t1=1, t2=2))
    task = Task.from_dict(args)
    assert task.url == args["url"]
    assert task.data == args["data"]

    args = dict(data=dict(t1=1, t2=2))
    pytest.raises(KeyError, Task.from_dict, **args)

    args = dict(url="url")
    task = Task.from_dict(args)
    assert task.url == args["url"]
    assert task.data is None


def test_task_to_dict():
    args = dict(url="url", data=dict(t1=1, t2=2))
    assert Task(**args).to_dict() == args
    args = dict(url="url", data=None)
    assert Task(**args).to_dict() == args


@pytest.mark.freeze_time("2016-12-23 00:00:00")
def test_throttle___init__():
    throttle = Throttle()
    assert throttle.fn is None
    assert throttle.time_started is not None
    assert throttle.time_last_modified is None
    assert throttle.state.sleep == 0.0001
    assert throttle.state.max_rps is None

    throttle = Throttle(sleep=1.23, max_rps=123, fn=lambda x: x + 1)
    assert throttle.fn(11) == 12
    assert throttle.time_started == time.time()
    assert throttle.time_last_modified is None
    assert throttle.state.sleep == 1.23
    assert throttle.state.max_rps == 123.0


def test_throttle___enter__():
    pass


def test_throttle___exit__():
    pass


@pytest.mark.freeze_time("2016-12-23 00:00:00")
def test_throttle_calculate(freezer):
    throttle = Throttle(sleep=1.23, max_rps=123)
    assert throttle.time_started == time.time()
    assert throttle.time_last_modified is None

    assert throttle.sleep
    assert throttle.state.iterations == 1
    assert throttle.time_last_modified == time.time()
    assert throttle.state.time_running == 0
    assert throttle.state.sleep == 1.23
    assert throttle.state.delta == 1.23
    assert throttle.state.rps == 0.0
    assert throttle.state.max_rps == 123.0

    freezer.move_to("2016-12-23 00:00:11")
    assert throttle.sleep
    assert throttle.state.iterations == 2
    assert throttle.time_last_modified == time.time()
    assert throttle.state.time_running == 11
    assert throttle.state.delta == 11.0 - 1.23
    assert throttle.state.rps == 1.0 / 11.0
    assert throttle.state.max_rps == 123.0
    assert throttle.state.sleep == (1.0 / (11.0 / 1.23) / 123.0)

    freezer.move_to("2016-12-23 00:00:00")
    throttle = Throttle(sleep=1.23, max_rps=None, fn=lambda x: x.sleep + 100)
    assert throttle.time_started == time.time()
    assert throttle.time_last_modified is None

    assert throttle.sleep
    assert throttle.state.iterations == 1
    assert throttle.time_last_modified == time.time()
    assert throttle.state.time_running == 0
    assert throttle.state.sleep == 0.0001
    assert throttle.state.delta == 1.23
    assert throttle.state.rps == 0.0
    assert throttle.state.max_rps is None

    freezer.move_to("2016-12-23 00:00:11")
    assert throttle.sleep
    assert throttle.state.iterations == 2
    assert throttle.time_last_modified == time.time()
    assert throttle.state.time_running == 11
    assert throttle.state.delta == 11.0 - 0.0001
    assert throttle.state.rps == 1.0 / 11.0
    assert throttle.state.max_rps is None
    assert throttle.state.sleep == 100.0 + 0.0001


def test_throttle_to_dict():
    throttle = Throttle()
    assert throttle.to_dict() == dict(iterations=0, sleep=0.0001, delta=0.0001, time=0.0001 * 2, rps=0)

    throttle = Throttle(sleep=1.23, max_rps=123, fn=lambda x: x.sleep + 100)
    assert throttle.to_dict() == dict(iterations=0, sleep=1.23, delta=1.23, time=1.23 * 2, rps=0)

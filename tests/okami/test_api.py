from collections import namedtuple

import pytest

from okami.api import Task, Item, Stats, State
from tests.factory import Factory


def test_downloader_process(factory: Factory):
    print("NotImplemented: test_downloader_process")


def test_item_to_dict(factory: Factory):
    pytest.raises(NotImplementedError, Item().to_dict)


def test_state__init__(factory: Factory):
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


def test_state_to_dict(factory: Factory):
    args = dict(sleep=1.23, max_rps=12.34)
    state = State(**args)
    assert state.to_dict() == dict(
        iterations=0,
        sleep=args["sleep"],
        delta=args["sleep"],
        time=args["sleep"] * 2,
        rps=0.0,
    )
    args = dict(sleep=1.23, max_rps=None)
    state = State(**args)
    assert state.to_dict() == dict(
        iterations=0,
        sleep=0.0001,
        delta=args["sleep"],
        time=args["sleep"] + 0.0001,
        rps=0.0,
    )


def test_stats__init__(factory: Factory):
    args = dict(
        times=dict(t1=1, t2=2),
        tasks=dict(t1=1, t2=2),
        items=dict(i1=1, i2=2),
        state=dict(s1=1, s2=2),
    )
    stats = Stats(**args)
    assert stats.times == args["times"]
    assert stats.tasks == args["tasks"]
    assert stats.items == args["items"]
    assert stats.state == args["state"]


def test_stats_from_dict(factory: Factory):
    args = dict(
        times=dict(t1=1, t2=2),
        tasks=dict(t1=1, t2=2),
        items=dict(i1=1, i2=2),
        state=dict(s1=1, s2=2),
    )
    stats = Stats.from_dict(args)
    assert stats.times == args["times"]
    assert stats.tasks == args["tasks"]
    assert stats.items == args["items"]
    assert stats.state == args["state"]
    assert stats.to_dict() == args


def test_stats_to_dict(factory: Factory):
    args = dict(
        times=dict(t1=1, t2=2),
        tasks=dict(t1=1, t2=2),
        items=dict(i1=1, i2=2),
        state=dict(s1=1, s2=2),
    )
    assert Stats(**args).to_dict() == args


def test_task___eq__(factory: Factory):
    assert Task(url="url") == Task(url="url")
    assert Task(url="url", data=1) == Task(url="url", data=1)


def test_task___hash__(factory: Factory):
    assert hash(Task(url="url")) == hash(("url", None))
    assert hash(Task(url="url")) != hash(("url"))
    assert hash(Task(url="url", data=1)) == hash(("url", 1))
    assert hash(Task(url="url", data=None)) == hash(("url", None))
    assert 2 == len({Task(url="url"), Task(url="url"), Task(url="url2")})
    assert 2 == len({Task(url="url", data=1), Task(url="url", data=1), Task(url="url", data=2)})


def test_task___ne__(factory: Factory):
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


def test_task_from_dict(factory: Factory):
    args = dict(
        url="url",
        data=dict(t1=1, t2=2),
    )
    task = Task.from_dict(args)
    assert task.url == args["url"]
    assert task.data == args["data"]

    args = dict(
        data=dict(t1=1, t2=2),
    )
    pytest.raises(KeyError, Task.from_dict, **args)

    args = dict(
        url="url",
    )
    task = Task.from_dict(args)
    assert task.url == args["url"]
    assert task.data is None


def test_task_to_dict(factory: Factory):
    args = dict(
        url="url",
        data=dict(t1=1, t2=2),
    )
    assert Task(**args).to_dict() == args
    args = dict(
        url="url",
        data=None,
    )
    assert Task(**args).to_dict() == args


def test_throttle___enter__(factory: Factory):
    print("NotImplemented: test_throttle___enter__")


def test_throttle___exit__(factory: Factory):
    print("NotImplemented: test_throttle___exit__")


def test_throttle_calculate(factory: Factory):
    print("NotImplemented: test_throttle_calculate")


def test_throttle_to_dict(factory: Factory):
    print("NotImplemented: test_throttle_to_dict")

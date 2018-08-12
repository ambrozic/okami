import time

import pytest

from okami.api import Task
from okami.storage import BaseStorage, Storage, queue


def test_base_storage___init__():
    base_storage = BaseStorage(name=None)
    assert base_storage.name is None


def test_base_storage_to_dict():
    base_storage = BaseStorage(name="storage")
    assert base_storage.to_dict() == dict()


def test_base_storage_finalise():
    base_storage = BaseStorage(name=None)
    assert base_storage.finalise() is None


def test_base_storage_get_info_time_started():
    base_storage = BaseStorage(name=None)
    with pytest.raises(NotImplementedError):
        base_storage.get_info_time_started()


def test_base_storage_set_info_time_started():
    base_storage = BaseStorage(name=None)
    with pytest.raises(NotImplementedError):
        base_storage.set_info_time_started(value=1)


def test_base_storage_get_info_time_running():
    base_storage = BaseStorage(name=None)
    with pytest.raises(NotImplementedError):
        base_storage.get_info_time_running()


def test_base_storage_get_info_items_processed():
    base_storage = BaseStorage(name=None)
    with pytest.raises(NotImplementedError):
        base_storage.get_info_items_processed()


def test_base_storage_add_info_items_processed():
    base_storage = BaseStorage(name=None)
    with pytest.raises(NotImplementedError):
        base_storage.add_info_items_processed(value=1)


def test_base_storage_get_info_items_failed():
    base_storage = BaseStorage(name=None)
    with pytest.raises(NotImplementedError):
        base_storage.get_info_items_failed()


def test_base_storage_add_info_items_failed():
    base_storage = BaseStorage(name=None)
    with pytest.raises(NotImplementedError):
        base_storage.add_info_items_failed(value=1)


def test_base_storage_get_tasks_queued():
    base_storage = BaseStorage(name=None)
    with pytest.raises(NotImplementedError):
        base_storage.get_tasks_queued()


def test_base_storage_add_tasks_queued():
    base_storage = BaseStorage(name=None)
    with pytest.raises(NotImplementedError):
        base_storage.add_tasks_queued(values=[1, 2, 3])


def test_base_storage_tasks_queued_is_empty():
    base_storage = BaseStorage(name=None)
    with pytest.raises(NotImplementedError):
        base_storage.tasks_queued_is_empty()


def test_base_storage_get_tasks_processed():
    base_storage = BaseStorage(name=None)
    with pytest.raises(NotImplementedError):
        base_storage.get_tasks_processed()


def test_base_storage_add_tasks_processed():
    base_storage = BaseStorage(name=None)
    with pytest.raises(NotImplementedError):
        base_storage.add_tasks_processed(values=[1, 2, 3])


def test_base_storage_get_tasks_failed():
    base_storage = BaseStorage(name=None)
    with pytest.raises(NotImplementedError):
        base_storage.get_tasks_failed()


def test_base_storage_add_tasks_failed():
    base_storage = BaseStorage(name=None)
    with pytest.raises(NotImplementedError):
        base_storage.add_tasks_failed(values=[1, 2, 3])


def test_storage_add_info_items_failed():
    pass


def test_storage_add_info_items_processed():
    pass


def test_storage_add_tasks_failed():
    storage = Storage()
    with pytest.raises(ValueError):
        storage.add_tasks_failed(values=[1, 2, 3])


def test_storage_add_tasks_processed():
    storage = Storage()
    assert storage.get_tasks_processed() == set()

    s1 = {Task(url="a"), Task(url="b"), Task(url="c")}
    s2 = {Task(url="c"), Task(url="d"), Task(url="e")}
    s3 = {Task(url=1), Task(url=2), Task(url=3)}
    storage.add_tasks_processed(values=s1)
    storage.add_tasks_processed(values=s2)
    storage.add_tasks_processed(values=s3)
    assert storage.get_tasks_processed() == s1 | s2 | s3
    with pytest.raises(ValueError):
        storage.add_tasks_processed(values=[1, 2, 3])


def test_storage_add_tasks_queued():
    storage = Storage()
    pytest.raises(queue.Empty, storage.get_tasks_queued)

    s1 = {Task(url="a"), Task(url="b"), Task(url="c")}
    storage.add_tasks_queued(s1)
    assert s1 == {storage.get_tasks_queued() for _ in s1}

    s1 = {Task(url="a"), Task(url="b"), Task(url="c"), Task(url="d")}
    storage.add_tasks_queued(s1)
    assert Task(url="d") == storage.get_tasks_queued()
    pytest.raises(queue.Empty, storage.get_tasks_queued)
    with pytest.raises(ValueError):
        storage.add_tasks_queued(values=[1, 2, 3])


def test_storage_finalise():
    pass


def test_storage_get_info_items_failed():
    storage = Storage()
    assert storage.get_info_items_failed() == 0

    storage.add_info_items_failed(123)
    assert storage.get_info_items_failed() == 123
    assert isinstance(storage.get_info_items_failed(), int)

    storage.add_info_items_failed(123)
    assert storage.get_info_items_failed() == 123 + 123
    assert isinstance(storage.get_info_items_failed(), int)


def test_storage_get_info_items_processed():
    storage = Storage()
    assert storage.get_info_items_processed() == 0

    storage.add_info_items_processed(123)
    assert storage.get_info_items_processed() == 123
    assert isinstance(storage.get_info_items_processed(), int)

    storage.add_info_items_processed(123)
    assert storage.get_info_items_processed() == 123 + 123
    assert isinstance(storage.get_info_items_processed(), int)


@pytest.mark.freeze_time("2016-12-23 00:00:00")
def test_storage_get_info_time_running(freezer):
    storage = Storage()
    storage.set_info_time_started(value=time.time())
    assert storage.get_info_time_running() == 0.0
    freezer.move_to("2016-12-23 00:00:11")
    assert storage.get_info_time_running() == 11.0


def test_storage_get_info_time_started():
    storage = Storage()
    assert storage.get_info_time_started() is None

    storage.set_info_time_started(123)
    assert storage.get_info_time_started() == 123.0
    assert isinstance(storage.get_info_time_started(), float)


def test_storage_get_tasks_failed():
    storage = Storage()
    assert storage.get_tasks_failed() == set()

    s1 = {Task(url="a"), Task(url="b"), Task(url="c")}
    storage.add_tasks_failed(s1)
    assert storage.get_tasks_failed() == s1

    s2 = {Task(url="c"), Task(url="d"), Task(url="e")}
    storage.add_tasks_failed(s2)
    assert storage.get_tasks_failed() == s1 | s2

    s3 = {Task(url=1), Task(url=2), Task(url=3)}
    storage.add_tasks_failed(s3)
    assert storage.get_tasks_failed() == s1 | s2 | s3


def test_storage_get_tasks_processed():
    storage = Storage()
    assert storage.get_tasks_processed() == set()

    s1 = {Task(url="a"), Task(url="b"), Task(url="c")}
    storage.add_tasks_processed(values=s1)
    assert storage.get_tasks_processed() == s1

    s2 = {Task(url="c"), Task(url="d"), Task(url="e")}
    storage.add_tasks_processed(values=s2)
    assert storage.get_tasks_processed() == s1 | s2

    s3 = {Task(url=1), Task(url=2), Task(url=3)}
    storage.add_tasks_processed(values=s3)
    assert storage.get_tasks_processed() == s1 | s2 | s3


def test_storage_get_tasks_queued():
    storage = Storage()
    pytest.raises(queue.Empty, storage.get_tasks_queued)

    s1 = {"a", "b", "c"}
    storage.add_tasks_queued(s1)
    assert storage._tasks_queued.qsize() == 3
    assert s1 == {storage.get_tasks_queued() for _ in s1}
    pytest.raises(queue.Empty, storage.get_tasks_queued)
    assert storage._tasks_queued.qsize() == 0

    s2 = {"c", "d", "e"}
    storage.add_tasks_queued(s2)
    assert storage._tasks_queued.qsize() == 2
    assert {"d", "e"} == {storage.get_tasks_queued() for _ in range(2)}
    pytest.raises(queue.Empty, storage.get_tasks_queued)

    storage.add_tasks_queued({1, 2, 3})
    assert storage._tasks_queued.qsize() == 3
    assert {1, 2, 3} == {storage.get_tasks_queued() for _ in range(3)}
    pytest.raises(queue.Empty, storage.get_tasks_queued)
    assert storage._tasks_queued.qsize() == 0


@pytest.mark.freeze_time("2016-12-23 00:00:00")
def test_storage_set_info_time_started(freezer):
    storage = Storage()
    ts = time.time()
    assert storage.get_info_time_running() == 0.0
    storage.set_info_time_started(value=ts)
    assert storage.get_info_time_started() == ts
    freezer.move_to("2016-12-23 00:00:11")
    assert storage.get_info_time_started() == ts
    assert storage.get_info_time_running() == 11.0


def test_storage_tasks_queued_is_empty():
    storage = Storage()
    assert storage.tasks_queued_is_empty()
    assert isinstance(storage.tasks_queued_is_empty(), bool)

    storage.add_tasks_queued({i for i in "abc"})
    assert not storage.tasks_queued_is_empty()
    assert isinstance(storage.tasks_queued_is_empty(), bool)


def test_storage_to_dict():
    storage = Storage()
    assert storage.to_dict() == dict(
        times_running=0.0, tasks_queued=0, tasks_processed=0, tasks_failed=0, items_processed=0, items_failed=0
    )

    storage.add_tasks_queued(values={1, 2, 3})
    storage.add_tasks_processed(values={11, 22, 33})
    storage.add_tasks_failed(values={111, 222, 333})
    assert storage.to_dict() == dict(
        times_running=0.0, tasks_queued=3, tasks_processed=6, tasks_failed=3, items_processed=0, items_failed=0
    )

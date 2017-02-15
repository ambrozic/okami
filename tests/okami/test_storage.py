import pytest

from okami.api import Task
from okami.storage import queue, LocalStorage, RedisStorage
from tests.factory import Factory


def test_local_storage_add_info_items_failed(factory: Factory):
    pass


def test_local_storage_add_info_items_processed(factory: Factory):
    pass


def test_local_storage_add_tasks_failed(factory: Factory):
    pass


def test_local_storage_add_tasks_processed(factory: Factory):
    storage = LocalStorage()
    assert storage.get_tasks_processed() == set()

    s1 = {Task(url="a"), Task(url="b"), Task(url="c")}
    s2 = {Task(url="c"), Task(url="d"), Task(url="e")}
    s3 = {Task(url=1), Task(url=2), Task(url=3)}
    storage.add_tasks_processed(values=s1)
    storage.add_tasks_processed(values=s2)
    storage.add_tasks_processed(values=s3)
    assert storage.get_tasks_processed() == s1 | s2 | s3


def test_local_storage_add_tasks_queued(factory: Factory):
    storage = LocalStorage()
    pytest.raises(queue.Empty, storage.get_tasks_queued)

    s1 = {Task(url="a"), Task(url="b"), Task(url="c")}
    storage.add_tasks_queued(s1)
    assert s1 == {storage.get_tasks_queued() for _ in s1}

    s1 = {Task(url="a"), Task(url="b"), Task(url="c"), Task(url="d")}
    storage.add_tasks_queued(s1)
    assert Task(url="d") == storage.get_tasks_queued()
    pytest.raises(queue.Empty, storage.get_tasks_queued)


def test_local_storage_filter(factory: Factory):
    pass


def test_local_storage_finalise(factory: Factory):
    pass


def test_local_storage_get_info_items_failed(factory: Factory):
    storage = LocalStorage()
    assert storage.get_info_items_failed() == 0

    storage.add_info_items_failed(123)
    assert storage.get_info_items_failed() == 123
    assert isinstance(storage.get_info_items_failed(), int)

    storage.add_info_items_failed(123)
    assert storage.get_info_items_failed() == 123 + 123
    assert isinstance(storage.get_info_items_failed(), int)


def test_local_storage_get_info_items_processed(factory: Factory):
    storage = LocalStorage()
    assert storage.get_info_items_processed() == 0

    storage.add_info_items_processed(123)
    assert storage.get_info_items_processed() == 123
    assert isinstance(storage.get_info_items_processed(), int)

    storage.add_info_items_processed(123)
    assert storage.get_info_items_processed() == 123 + 123
    assert isinstance(storage.get_info_items_processed(), int)


def test_local_storage_get_info_time_initialised(factory: Factory):
    storage = LocalStorage()
    assert storage.get_info_time_initialised() is None

    storage.set_info_time_initialised(123)
    assert storage.get_info_time_initialised() == 123.0
    assert isinstance(storage.get_info_time_initialised(), float)


def test_local_storage_get_info_time_initialising(factory: Factory):
    pass


def test_local_storage_get_info_time_running(factory: Factory):
    pass


def test_local_storage_get_info_time_started(factory: Factory):
    storage = LocalStorage()
    assert storage.get_info_time_started() is None

    storage.set_info_time_started(123)
    assert storage.get_info_time_started() == 123.0
    assert isinstance(storage.get_info_time_started(), float)


def test_local_storage_get_tasks_failed(factory: Factory):
    storage = LocalStorage()
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


def test_local_storage_get_tasks_processed(factory: Factory):
    storage = LocalStorage()
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


def test_local_storage_get_tasks_queued(factory: Factory):
    storage = LocalStorage()
    pytest.raises(queue.Empty, storage.get_tasks_queued)

    s1 = {"a", "b", "c"}
    storage.add_tasks_queued(s1)
    assert s1 == {storage.get_tasks_queued() for _ in s1}
    pytest.raises(queue.Empty, storage.get_tasks_queued)

    s2 = {"c", "d", "e"}
    storage.add_tasks_queued(s2)
    assert {"d", "e"} == {storage.get_tasks_queued() for _ in range(2)}
    pytest.raises(queue.Empty, storage.get_tasks_queued)

    storage.add_tasks_queued({1, 2, 3})
    assert {1, 2, 3} == {storage.get_tasks_queued() for _ in range(3)}
    pytest.raises(queue.Empty, storage.get_tasks_queued)


def test_local_storage_initialise(factory: Factory):
    pass


def test_local_storage_set_info_time_initialised(factory: Factory):
    pass


def test_local_storage_set_info_time_started(factory: Factory):
    pass


def test_local_storage_tasks_queued_is_empty(factory: Factory):
    storage = LocalStorage()
    assert storage.tasks_queued_is_empty()
    assert isinstance(storage.tasks_queued_is_empty(), bool)

    storage.add_tasks_queued({i for i in "abc"})
    assert not storage.tasks_queued_is_empty()
    assert isinstance(storage.tasks_queued_is_empty(), bool)


def test_local_storage_to_dict(factory: Factory):
    pass


def test_redis_storage_add_info_items_failed(factory: Factory):
    pass


def test_redis_storage_add_info_items_processed(factory: Factory):
    pass


def test_redis_storage_add_tasks_failed(factory: Factory, storage: RedisStorage):
    assert storage.get_tasks_failed() == set()

    s1 = {Task(url="a"), Task(url="b"), Task(url="c")}
    s2 = {Task(url="c"), Task(url="d"), Task(url="e")}
    s3 = {Task(url=1), Task(url=2), Task(url=3)}
    storage.add_tasks_failed(values=s1)
    storage.add_tasks_failed(values=s2)
    storage.add_tasks_failed(values=s3)
    assert storage.get_tasks_failed() == s1 | s2 | s3


def test_redis_storage_add_tasks_processed(factory: Factory, storage: RedisStorage):
    assert storage.get_tasks_processed() == set()

    s1 = {Task(url="a"), Task(url="b"), Task(url="c")}
    s2 = {Task(url="c"), Task(url="d"), Task(url="e")}
    s3 = {Task(url=1), Task(url=2), Task(url=3)}
    storage.add_tasks_processed(values=s1)
    storage.add_tasks_processed(values=s2)
    storage.add_tasks_processed(values=s3)
    assert storage.get_tasks_processed() == s1 | s2 | s3


def test_redis_storage_add_tasks_queued(factory: Factory, storage: RedisStorage):
    s1 = {Task(url="a"), Task(url="b"), Task(url="c")}
    storage.add_tasks_queued(s1)
    assert s1 == {storage.get_tasks_queued() for _ in s1}

    s1 = {Task(url="a"), Task(url="b"), Task(url="c"), Task(url="d")}
    storage.add_tasks_queued(s1)
    assert Task(url="d") == storage.get_tasks_queued()


def test_redis_storage_filter(factory: Factory, storage: RedisStorage):
    s1 = {Task(url="a"), Task(url="b"), Task(url="c")}
    s2 = {Task(url="c"), Task(url="d"), Task(url="e")}
    storage.add_tasks_processed(values=s1)
    assert storage.filter(values=s2) == s2 - s1
    assert storage.filter(values=s2) == {Task(url="d"), Task(url="e")}


def test_redis_storage_finalise(factory: Factory):
    pass


def test_redis_storage_get_info_items_failed(factory: Factory):
    pass


def test_redis_storage_get_info_items_processed(factory: Factory):
    pass


def test_redis_storage_get_info_time_initialised(factory: Factory):
    pass


def test_redis_storage_get_info_time_initialising(factory: Factory):
    pass


def test_redis_storage_get_info_time_running(factory: Factory):
    pass


def test_redis_storage_get_info_time_started(factory: Factory):
    pass


def test_redis_storage_get_tasks_failed(factory: Factory, storage: RedisStorage):
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


def test_redis_storage_get_tasks_processed(factory, storage: RedisStorage):
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


def test_redis_storage_get_tasks_queued(factory: Factory, storage: RedisStorage):
    s1 = {"a", "b", "c"}
    storage.add_tasks_queued(s1)
    assert s1 == {storage.get_tasks_queued() for _ in s1}

    s2 = {"c", "d", "e"}
    storage.add_tasks_queued(s2)
    assert {"d", "e"} == {storage.get_tasks_queued() for _ in range(2)}

    storage.add_tasks_queued({1, 2, 3})
    assert {1, 2, 3} == {storage.get_tasks_queued() for _ in range(3)}

    # will block for 1 second
    pytest.raises(queue.Empty, storage.get_tasks_queued)


def test_redis_storage_initialise(factory: Factory):
    pass


def test_redis_storage_set_info_time_initialised(factory: Factory):
    pass


def test_redis_storage_set_info_time_started(factory: Factory):
    pass


def test_redis_storage_tasks_queued_is_empty(factory: Factory):
    pass


def test_redis_storage_to_dict(factory: Factory):
    pass

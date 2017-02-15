import os

import pytest

from tests.factory import Factory

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="session")
def factory():
    return Factory()


@pytest.fixture(scope="function")
def storage():
    try:
        import redis
    except ImportError:
        pytest.skip()

    try:
        from okami.storage import RedisStorage
        storage = RedisStorage(name="test", url="redis://localhost:6379/0")
        storage.db.flushall()
        yield storage
        storage.db.flushall()
    except redis.exceptions.ConnectionError:
        pytest.skip()

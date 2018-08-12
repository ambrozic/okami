import os

os.environ["OKAMI_SETTINGS"] = "tests.settings"  # noqa

import asyncio
from functools import partial

import pytest
from aiohttp.test_utils import TestServer
from sqlitedict import SqliteDict

from okami import settings
from tests.factory import Factory

settings.configure()


@pytest.fixture(scope="session")
def factory():
    return Factory()


@pytest.fixture(scope="function")
def db(tmpdir):
    filename = os.path.join(str(tmpdir), "okami.sqlite")
    database = SqliteDict(filename=filename, autocommit=True)
    yield database
    database.close()


@pytest.fixture(scope="function")
def coro():
    return asyncio.coroutine


@pytest.fixture(scope="function")
def server(app=None, port=8888):
    return partial(TestServer, app=app, port=port)

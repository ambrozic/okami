from unittest import mock

import pytest

from okami import constants
from okami.api import BaseSpider, Response, Request, Task
from okami.exceptions import SpiderException
from tests.factory import Factory


@pytest.mark.asyncio
async def test_base_spider():
    spider = BaseSpider()
    request = Request(url="url")
    response = mock.Mock(text="<html></html>")

    assert spider.name is None
    assert spider.urls is None

    with pytest.raises(NotImplementedError):
        await spider.items(task=object(), response=response)

    with pytest.raises(SpiderException):
        await spider.process(task=object(), response=response)

    assert spider.request() == dict()

    with pytest.raises(NotImplementedError):
        await spider.session(request=request)
    assert await spider.hash(task=object(), response=response) is None

    spider.urls = dict(allow=["allow"], avoid=["avoid"])
    assert await spider.tasks(task=object(), response=response) == set()


@pytest.mark.asyncio
async def test_base_spider_items():
    spider = BaseSpider()
    with pytest.raises(NotImplementedError):
        await spider.items(task=object(), response=mock.Mock(text="<html></html>"))


@pytest.mark.asyncio
async def test_base_spider_process():
    spider = BaseSpider()
    with pytest.raises(SpiderException):
        await spider.process(task=object(), response=mock.Mock(text="<html></html>"))


@pytest.mark.asyncio
async def test_base_spider_hash():
    assert await BaseSpider().hash(task=mock.Mock(), response=mock.Mock()) is None


@pytest.mark.asyncio
async def test_base_spider_request():
    assert BaseSpider().request() == dict()


@pytest.mark.asyncio
async def test_base_spider_session():
    with pytest.raises(NotImplementedError):
        await BaseSpider().session(request=Request(url="url"))


@pytest.mark.asyncio
async def test_base_spider_tasks(factory: Factory):
    spider = factory.obj.spider.create()
    task = Task(url="http://localhost/")
    response = Response(
        url="http://localhost/",
        version="version",
        status=constants.status.OK,
        reason="reason",
        headers=dict(a=1),
        text="<html>"
             "<a href='/start/'>start</a>"
             "<a href='/allow/'>allow</a><a href='/allow1/'>allow1</a><a href='/allow2/'>allow2</a>"
             "<a href='/avoid/'>avoid</a><a href='/avoid1/'>avoid1</a><a href='/avoid2/'>avoid2</a>"
             "</html>",
    )
    assert await spider.tasks(task=task, response=response) == {
        Task(url="http://localhost/allow/"),
        Task(url="http://localhost/allow2/"),
        Task(url="http://localhost/allow1/"),
    }

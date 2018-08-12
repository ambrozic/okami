from unittest import mock

import pytest

from okami import Task
from okami.pipeline import Cache, Cleaner, Images, Parser, Pipeline, Settings, Tasks
from tests.factory import Factory


def test_pipeline___init__():
    controller = object()
    middleware = Pipeline(controller=controller)
    assert middleware.controller is controller


@pytest.mark.asyncio
async def test_pipeline_initialise():
    pipeline = Pipeline(controller=object())
    assert await pipeline.initialise() is None


@pytest.mark.asyncio
async def test_pipeline_process():
    pipeline = Pipeline(controller=object())
    with pytest.raises(NotImplementedError):
        await pipeline.process(something=object())


@pytest.mark.asyncio
async def test_pipeline_finalise():
    pipeline = Pipeline(controller=object())
    assert await pipeline.finalise() is None


@pytest.mark.asyncio
async def test_cache_process(factory: Factory):
    spider = factory.obj.spider.create()
    pipeline = Cache(controller=object())
    assert await pipeline.process(spider=spider) is spider


@pytest.mark.asyncio
async def test_cleaner_process(factory: Factory):
    items = [[factory.obj.product.create(), factory.obj.product.create()]]
    pipeline = Cleaner(controller=object())
    assert await pipeline.process(items=items) is items


@pytest.mark.asyncio
async def test_images_process():
    items = [mock.Mock(images=[1, 2, 3]), mock.Mock(images=[11, 22, 33])]
    pipeline = Images(controller=object())
    assert await pipeline.process(items=items) is items


@pytest.mark.asyncio
async def test_parser_process(factory: Factory):
    items = [[factory.obj.product.create(), factory.obj.product.create()]]
    pipeline = Parser(controller=object())
    assert await pipeline.process(items=items) is items


@pytest.mark.asyncio
async def test_settings_process(factory: Factory):
    spider = factory.obj.spider.create()
    pipeline = Settings(controller=object())
    assert await pipeline.process(spider=spider) is spider


@pytest.mark.asyncio
async def test_tasks_process():
    tasks = {Task(url="url1"), Task(url="url2")}
    pipeline = Tasks(controller=object())
    assert await pipeline.process(tasks=tasks) is tasks

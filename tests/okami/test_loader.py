import pytest

from okami import loader, Spider, settings
from okami.example import Example
from okami.exceptions import NoSuchSpiderException
from tests.factory import Factory


def test_get_class():
    assert Spider == loader.get_class("okami.Spider")
    assert Example == loader.get_class("okami.example.Example")
    assert Factory == loader.get_class("tests.factory.Factory")


def test_get_spider_class_by_name():
    assert Example == loader.get_spider_class_by_name(name="example.com")
    with pytest.raises(NoSuchSpiderException) as e:
        loader.get_spider_class_by_name(name="no-such-spider")
    assert "okami.exceptions.NoSuchSpiderException: no-such-spider" in str(e)


def test_get_spiders_classes():
    for package in settings.SPIDERS:
        assert {"example.com": Example} == loader.get_spiders_classes(entry_point_name=package)
    assert {"example.com": Example} == loader.get_spiders_classes(entry_point_name=None)


def test_is_spider(factory: Factory):
    assert False is loader.is_spider(obj=factory.obj.spider.create())
    assert True is loader.is_spider(obj=Spider)
    assert False is loader.is_spider(obj=factory.obj.product.create())
    assert False is loader.is_spider(obj=Factory)
    assert False is loader.is_spider(obj=object())
    assert False is loader.is_spider(obj=object)

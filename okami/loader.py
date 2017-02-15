import inspect
import logging
import pkgutil

from okami.api import Spider
from okami.configuration import settings
from okami.exceptions import NoSuchSpiderException

log = logging.getLogger(__name__)


def is_spider(obj):
    return inspect.isclass(obj) and issubclass(obj, Spider) and getattr(obj, "name", None)


def get_class(path_name):
    path = ".".join(path_name.split(".")[:-1])
    clazz = path_name.split(".")[-1]
    module = inspect.importlib.import_module(path)
    return getattr(module, clazz)


def get_spider_class_by_name(name):
    for path in settings.SPIDERS:
        module = inspect.importlib.import_module(path)
        for importer, modname, ispkg in pkgutil.walk_packages(path=module.__path__):
            if not ispkg:
                mod = inspect.importlib.import_module(module.__name__ + "." + modname)
                for _, cls in inspect.getmembers(mod, lambda m: is_spider(m)):
                    try:
                        if name and getattr(cls, "name", None) == name:
                            return cls
                    except AttributeError:
                        pass
    raise NoSuchSpiderException(name)


def get_spiders_classes(entry_point_name=None):
    discovered = dict()
    if not entry_point_name:
        entry_point_name = __name__.split(".")[0]

    def load_module(module_name):
        module = inspect.importlib.import_module(module_name)
        for importer, modname, ispkg in pkgutil.walk_packages(path=module.__path__):
            mod = inspect.importlib.import_module(module.__name__ + "." + modname)
            if ispkg:
                load_module(mod.__name__)
            else:
                for name, obj in inspect.getmembers(mod):
                    if is_spider(obj) and mod.__name__ == obj.__module__:
                        try:
                            sn = getattr(obj, "name", None)
                            if sn in discovered:
                                raise Exception("Duplicate spider '{}': {} and {}".format(sn, obj, discovered[sn]))
                            discovered[sn] = obj
                        except AttributeError:
                            pass

    load_module(module_name=entry_point_name)
    return discovered

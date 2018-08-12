__version__ = "0.2.0"

from .cfg import Settings  # noqa

settings = Settings()

from .api import Downloader, Item, Response, Request, Spider, Task, Throttle  # noqa
from .storage import Storage  # noqa

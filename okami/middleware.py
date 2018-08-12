import hashlib
import json
import logging
import os
import time
from pathlib import Path

import aiohttp
from sqlitedict import SqliteDict

from okami import settings, utils

log = logging.getLogger(__name__)


class Middleware:
    """
    Base Middleware <okami.middleware.Middleware>

    :param controller: Controller <okami.engine.Controller>
    """

    def __init__(self, controller):
        self.controller = controller

    async def initialise(self):
        """
        Executed at the beginning of scraping process. Exceptions should be caught or entire middleware terminates.
        """
        pass

    async def before(self, **kwargs):
        """
        Processes passed object. Exceptions should be caught or entire middleware terminates.

        :param kwargs:
        :returns: something: Any
        """
        raise NotImplementedError

    async def after(self, **kwargs):
        """
        Processes passed object. Exceptions should be caught or entire middleware terminates.

        :param kwargs
        :returns: kwargs
        """
        raise NotImplementedError

    async def finalise(self):
        """
        Executed at the end of scraping process. Exceptions should be caught or entire middleware terminates.
        """
        pass


class Delta(Middleware):
    """
    Delta <okami.middleware.Delta>

    :param controller: Controller <okami.engine.Controller>
    """

    def __init__(self, controller):
        super().__init__(controller)
        self.db = None
        self.filename = None
        self.key_added = "delta/added"
        self.key_skipped = "delta/skipped"

    async def initialise(self):
        if not settings.DELTA_ENABLED:
            return
        self.filename = os.path.join(settings.DELTA_PATH or ".", "{}.json".format(self.controller.spider.name))
        path = Path(self.filename)
        path.parent.mkdir(exist_ok=True)
        path.touch(exist_ok=True)
        with open(path, "r") as f:
            self.db = json.loads(f.read() or "{}")
        self.controller.stats.set(self.key_added, 0)
        self.controller.stats.set(self.key_skipped, 0)

    async def after(self, task, response, tasks, items):
        if self.db is None:
            return tasks, items

        if items:
            self.db[await self.to_key(task=task, response=response)] = str(time.time())
            self.controller.stats.incr(key=self.key_added)

        _tasks = set()
        for t in tasks:
            if await self.to_key(task=t, response=response) in self.db:
                log.info("Skipped visited url - %s", t.url)
                self.controller.stats.incr(key=self.key_skipped)
                continue
            _tasks.add(t)

        return _tasks, items

    async def finalise(self):
        if self.db is not None:
            with open(self.filename, "w") as f:
                json.dump(obj=self.db, fp=f)

    async def to_key(self, task, response):
        key = await self.controller.spider.hash(task=task, response=response)
        return key or hashlib.sha1(task.url.encode()).hexdigest()


class DeltaSqlite(Middleware):
    """
    DeltaSqlite <okami.middleware.DeltaSqlite>

    :param controller: Controller <okami.engine.Controller>
    """

    def __init__(self, controller):
        super().__init__(controller)
        self.db = None
        self.filename = None
        self.key_added = "delta/added"
        self.key_skipped = "delta/skipped"

    async def initialise(self):
        if not settings.DELTA_ENABLED:
            return
        self.filename = os.path.join(settings.DELTA_PATH or ".", "{}.sqlite".format(self.controller.spider.name))
        self.db = SqliteDict(filename=self.filename, tablename="delta", autocommit=True)
        self.controller.stats.set(self.key_added, 0)
        self.controller.stats.set(self.key_skipped, 0)

    async def after(self, task, response, tasks, items):
        if self.db is None:
            return tasks, items

        if items:
            self.db[await self.to_key(task=task, response=response)] = str(time.time())
            self.controller.stats.incr(key=self.key_added)

        _tasks = set()
        for t in tasks:
            if await self.to_key(task=t, response=response) in self.db:
                log.info("Skipped visited url - %s", t.url)
                self.controller.stats.incr(key=self.key_skipped)
                continue
            _tasks.add(t)

        return _tasks, items

    async def finalise(self):
        if self.db is not None:
            self.db.close()

    async def to_key(self, task, response):
        key = await self.controller.spider.hash(task=task, response=response)
        return key or hashlib.sha1(task.url.encode()).hexdigest()


class Logger(Middleware):
    """
    Logger <okami.middleware.Logger>
    """

    async def after(self, response):
        data = self.controller.stats.collect()
        print(
            "\033[94mOkami\033[0m: "
            "\033[91m{}\033[0m - "
            "delta=\033[92m{:.4f}\033[0m "
            "sleep=\033[92m{:.4f}\033[0m "
            "time=\033[92m{:.4f}\033[0m "
            "rps=\033[92m{:<6.2f}\033[0m "
            "i=\033[92m{}\033[0m - "
            "\033[96m{}\033[0m/\033[92m{}\033[0m/\033[91m{}\033[0m/\033[94m{}\033[0m - \033[96m{:.2f}s\033[0m".format(
                self.controller.spider.name,
                data.get("throttle/delta", 0),
                data.get("throttle/sleep", 0),
                data.get("throttle/time", 0),
                data.get("throttle/rps", 0),
                data.get("throttle/iterations", 0),
                data.get("storage/tasks_queued", 0),
                data.get("storage/tasks_processed", 0),
                data.get("storage/tasks_failed", 0),
                data.get("storage/items_processed", 0),
                data.get("storage/times_running", 0),
            )
        )
        return response

    async def finalise(self):
        utils.pprint(obj=self.controller.stats.collect())


class Headers(Middleware):
    """
    Headers <okami.middleware.Headers>
    """

    async def before(self, request):
        """
        Processes passed Request <okami.Request>.
        Exceptions should be caught or entire middleware terminates.

        :param request: Request <okami.Request>
        :returns: altered passed Request <okami.Request>
        """
        if not request.headers:
            request.headers.update({"User-Agent": settings.USER_AGENT})
        return request


class Session(Middleware):
    """
    Session <okami.middleware.Session>
    """

    async def before(self, request):
        """
        Processes passed Request <okami.Request>.
        Exceptions should be caught or entire middleware terminates.

        :param request: Request <okami.Request>
        :returns: altered passed Request <okami.Request>
        """
        if not self.controller.session or self.controller.session.closed:
            try:
                self.controller.session = await self.controller.spider.session(request=request)
            except NotImplementedError:
                connector = aiohttp.TCPConnector(
                    limit=settings.CONN_MAX_CONCURRENT_CONNECTIONS,
                    verify_ssl=settings.CONN_VERIFY_SSL,
                )
                self.controller.session = aiohttp.ClientSession(connector=connector)
        return request

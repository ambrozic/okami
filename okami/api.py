import logging
import time

import lxml.html

from okami import constants, settings, signals, utils
from okami.exceptions import SpiderException

log = logging.getLogger(__name__)


class BaseSpider:
    """
    BaseSpider <okami.api.BaseSpider>

    :cvar name: unique spider name
    :cvar urls: (dictionary)
    """

    name = None
    urls = None

    async def items(self, task, response):
        """
        Processes Task <okami.Task> and Response <okami.Response>
        into a List[Item <okami.Item>].

        :param task: Task <okami.Task>
        :param response: Response <okami.Response>
        :returns: List[Item <okami.Item>]
        """
        raise NotImplementedError

    async def process(self, task, response):
        """
        :param task: Task <okami.Task>
        :param response: Response <okami.Response>
        :returns: tuple of (Set[Task <okami.Task>], List[Item <okami.Item>])
        """
        try:
            return (
                await self.tasks(task=task, response=response),
                await self.items(task=task, response=response),
            )
        except Exception as e:
            raise SpiderException(e) from e

    def request(self):
        """
        Defines a dictionary of extra arguments to pass in HTTP request.
        Check Downloader.process <okami.Downloader> method.

        :returns: (dictionary)
        """
        return dict()

    async def session(self, request):
        """
        Defines a session object for this Spider <okami.Spider>.
        Check Session.process <okami.pipeline.Session> method.

        Should be used for special cases like authentication handling etc.

        :param request: Request <okami.Request>
        :returns: aiohttp.ClientSession
        """
        raise NotImplementedError

    async def hash(self, task, response):
        """
        In case delta scrape mode is enabled and custom delta key functionality is required this method should be
        implemented.

        If None is returned, custom functionality is skipped.

        :param task: Task <okami.Task>
        :param response: Response <okami.Response>
        :returns: string or None
        """
        pass

    async def tasks(self, task, response):
        """
        Processes Response <okami.Response> into a Set[Task <okami.Task>].

        :param task: Task <okami.Task>
        :param response: Response <okami.Response>
        :returns: Set[Task <okami.Task>]
        """
        document = lxml.html.document_fromstring(html=response.text)
        urls = set()
        for xp in self.urls.get("allow", []):
            urls |= {utils.parse_domain_url(domain=str(response.url), url=str(u)) for u in document.xpath(xp)}
        for xp in self.urls.get("avoid", []):
            urls -= {utils.parse_domain_url(domain=str(response.url), url=str(u)) for u in document.xpath(xp)}
        return {Task(url=url) for url in urls}


class Downloader:
    """
    Downloader <okami.Downloader>

    :param controller: Controller <okami.engine.Controller>
    """

    def __init__(self, controller):
        self.controller = controller

    async def process(self, request):
        """
        Makes an actual HTTP request against a processing website's URL.

        :param request: Request <okami.Request>
        :returns: Response <okami.Response>
        """
        async with self.controller.session.request(
            **{
                **dict(
                    method=constants.method.GET,
                    url=request.url,
                    headers=request.headers,
                    allow_redirects=bool(settings.CONN_MAX_HTTP_REDIRECTS),
                    max_redirects=settings.CONN_MAX_HTTP_REDIRECTS,
                ),
                **self.controller.spider.request(),
            }
        ) as response:
            response = Response(
                url=response.url,
                version=response.version,
                status=response.status,
                reason=response.reason,
                headers=response.headers,
                text=await response.text(),
            )
            await signals.response_created.send(sender=self, response=response, response_created=True)
            return response


class Item:
    """
    Item <okami.Item>
    """

    def to_dict(self):
        """
        Converts Item <okami.Item> into dictionary representation

        :returns: (dictionary)
        """
        raise NotImplementedError


class Request:
    """
    Request <okami.Request>

    :param url: URL
    :param headers: (dictionary) of HTTP headers
    """

    def __init__(self, url, headers=None):
        self.url = url
        self.headers = headers or dict()


class Response:
    """
    Response <okami.Response>

    :param url: URL
    :param version: HTTP version
    :param status: HTTP status code
    :param reason: HTTP status text
    :param headers: (dictionary) of HTTP headers
    :param text: HTTP response body content
    """

    def __init__(self, url, version, status, reason, headers, text):
        self.url = url
        self.version = version
        self.status = status
        self.reason = reason
        self.headers = headers
        self.text = text


class Result:
    """
    Result <okami.api.Result>

    :param status: status <okami.constants.status>
    :param task: Task <okami.Task>
    :param tasks: Set[Task <okami.Task>]
    :param items: List[Item <okami.Item>]
    """

    __slots__ = ["status", "task", "tasks", "items"]

    def __init__(self, status, task, tasks, items):
        self.status = status
        self.task = task
        self.tasks = tasks
        self.items = items


class Spider(BaseSpider):
    """
    Spider <okami.Spider>
    """
    pass


class Stats:
    """
    Stats <okami.api.Stats>

    :param controller: Controller <okami.engine.Controller>
    """

    def __init__(self, controller):
        self.controller = controller
        self.data = dict()

    def collect(self):
        for k, v in self.controller.storage.to_dict().items():
            self.data["storage/{}".format(k)] = v
        for k, v in self.controller.throttle.to_dict().items():
            self.data["throttle/{}".format(k)] = v
        return self.data

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value

    def decr(self, key, value=1):
        self.data[key] -= value

    def incr(self, key, value=1):
        self.data[key] += value


class State:
    """
    State <okami.api.State>

    :param sleep: (float) sleep time between requests
    :param max_rps: (float) maximum number of requests per second

    :ivar iterations: (int) number of requests
    :ivar delta: (float) time taken between requests
    :ivar rps: (float) current number of request per second
    :ivar time_running: (float) time since start
    """

    def __init__(self, sleep, max_rps):
        self.iterations = 0
        self.sleep = float((sleep or 0.0001) if max_rps else 0.0001)
        self.delta = float(sleep or 0.0001)
        self.rps = 0.0
        self.max_rps = max_rps
        self.time_running = 0

    def to_dict(self):
        return dict(
            iterations=self.iterations,
            sleep=self.sleep,
            delta=self.delta,
            time=(self.delta or 0.0) + (self.sleep or 0.0),
            rps=self.rps,
        )


class Task:
    """
    Task <okami.Task>

    :param url: URL
    :param data: (dictionary)
    """

    __slots__ = ["url", "data"]

    def __init__(self, url, data=None):
        self.url = url
        self.data = data

    def __repr__(self):
        return "<Task url={}>".format(self.url)

    def __hash__(self):
        return hash((self.url, self.data))

    def __eq__(self, other):
        return isinstance(other, Task) and ((self.url, self.data) == (other.url, other.data))

    def __ne__(self, other):
        return not (self == other)

    @classmethod
    def from_dict(cls, data):
        """
        Creates Task <okami.Task> from dictionary 'data'

        :param data: (dictionary)
        :returns: Task <okami.Task>
        """
        return cls(
            url=data["url"],
            data=data.get("data"),
        )

    def to_dict(self):
        """
        Converts Task <okami.Task> into dictionary representation

        :returns: (dictionary)
        """
        return dict(
            url=self.url,
            data=self.data,
        )


class Throttle:
    """
    Throttle <okami.Throttle>

    :param sleep: (float) sleep time between requests
    :param max_rps: (float) maximum number of requests per second
    :param fn: (function) custom function for calculating sleep time

    :ivar time_started: (float) time at start
    :ivar time_last_modified: (float) time at last request
    :ivar state: State <okami.api.State>
    """

    def __init__(self, sleep=None, max_rps=None, fn=None):
        self.fn = fn
        self.time_started = time.time()
        self.time_last_modified = None
        self.state = State(sleep=sleep, max_rps=max_rps)

    def __enter__(self):
        return self

    def __exit__(self, exc, value, traceback):
        pass

    def to_dict(self):
        return self.state.to_dict()

    def calculate(self):
        now = time.time()
        diff = None
        self.state.iterations += 1

        if self.time_last_modified:
            diff = now - max(0, self.time_last_modified)
            self.state.rps = 1.0 / diff
            self.state.delta = diff - self.state.sleep

        self.time_last_modified = now
        self.state.time_running = now - self.time_started

        if not diff:
            return

        if self.state.max_rps:
            self.state.sleep = (1.0 / (diff / (self.state.sleep or 0.0001))) / float(self.state.max_rps)
            return

        if self.fn:
            self.state.sleep = self.fn(self.state)

    @property
    def sleep(self):
        self.calculate()
        return self.state.sleep

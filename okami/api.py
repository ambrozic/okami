import logging
import time

import lxml.html

from okami import constants, signals, utils
from okami.configuration import settings
from okami.exceptions import SpiderException

log = logging.getLogger(__name__)


class BaseSpider:
    """
    :class:`BaseSpider <okami.api.BaseSpider>` object

    :cvar name: unique spider name
    :cvar urls: (dictionary)

    .. code-block:: python

        class Example(Spider):
            name = "example.com"
            urls = dict(
                start=[],
                allow=[],
                avoid=[]
            )
    """

    name = None
    urls = None

    async def items(self, task, response):
        """
        Processes :class:`Response <okami.api.Response>` object into a list of :class:`Item <okami.Item>` objects.

        :param task: :class:`Task <okami.Task>` object
        :param response: :class:`Response <okami.api.Response>` object
        :returns: list of :class:`Item <okami.Item>` objects
        """
        raise NotImplementedError

    async def process(self, task, response):
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
        Check :class:`Downloader.process <okami.Downloader>` method.

        :returns: (dictionary)
        """
        return dict()

    def session(self):
        """
        Defines a session object for this :class:`Spider <okami.Spider>`.
        Check :class:`Session.process <okami.pipeline.Session>` method.

        Should be used for special cases like authentication handling etc.

        :returns: (list) of :class:`Item <okami.Item>` objects
        """
        raise NotImplementedError

    async def tasks(self, task, response):
        """
        Processes :class:`Response <okami.api.Response>` object into a list of :class:`Task <okami.Task>` objects.

        :param task: :class:`Task <okami.Task>` object
        :param response: :class:`Response <okami.api.Response>` object
        :returns: (list) of :class:`Task <okami.Task>` objects
        """
        document = lxml.html.document_fromstring(html=response.text)
        urls = set()
        for xp in self.urls.get("allow", []):
            urls |= {utils.parse_domain_url(domain=response.url, url=str(u)) for u in document.xpath(xp)}
        for xp in self.urls.get("avoid", []):
            urls -= {utils.parse_domain_url(domain=response.url, url=str(u)) for u in document.xpath(xp)}
        return {Task(url=url) for url in urls}


class Downloader:
    """
    :class:`Downloader <okami.Downloader>` object

    :param controller: :class:`Controller <okami.engine.Controller>` object
    """

    def __init__(self, controller):
        self.controller = controller

    async def process(self, request):
        """
        Makes an actual HTTP request against a processing website's URL.

        :param request: :class:`Request <okami.api.Request>` object
        :returns: :class:`Response <okami.api.Response>` object
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
    :class:`Item <okami.Item>` object
    """

    def to_dict(self):
        """
        Converts :class:`Item <okami.Item>` object into dictionary representation

        :returns: (dictionary)
        """
        raise NotImplementedError


class Request:
    """
    :class:`Request <okami.api.Request>` object

    :param url: URL
    :param headers: (dictionary) of HTTP headers
    """

    def __init__(self, url, headers=None):
        self.url = url
        self.headers = headers or dict()


class Response:
    """
    :class:`Response <okami.api.Response>` object

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
    :class:`Result <okami.api.Result>` object

    :param status: :class:`status <okami.constants.status>` object
    :param task: :class:`Task <okami.Task>` object
    :param tasks: (list) of :class:`Task <okami.Task>` objects
    :param items: (list) of :class:`Item <okami.Item>` objects
    """
    __slots__ = ["status", "task", "tasks", "items"]

    def __init__(self, status, task, tasks, items):
        self.status = status
        self.task = task
        self.tasks = tasks
        self.items = items


class Spider(BaseSpider):
    """:class:`Spider <okami.Spider>` object

    Take a look at this example :class:`Spider <okami.Spider>`.

    :cvar name: unique spider name
    :cvar urls: (dictionary)

    .. code-block:: python

        class Example(Spider):
            name = "example.com"
            urls = dict(
                start=[],
                allow=[],
                avoid=[]
            )
    """


class Stats:
    """
    :class:`Stats <okami.api.Stats>` object

    :param times: (dictionary)
    :param tasks: (dictionary)
    :param items: (dictionary)
    :param state: (dictionary)
    """
    __slots__ = ["times", "tasks", "items", "state"]

    def __init__(self, times, tasks, items, state):
        self.times = times
        self.tasks = tasks
        self.items = items
        self.state = state

    @classmethod
    def from_dict(cls, data):
        """
        Create new :class:`Stats <okami.api.Stats>` object from passed dictionary

        :param data: (dictionary)
        :returns: :class:`Stats <okami.api.Stats>` object
        """
        return cls(
            times=data.get("times", {}),
            tasks=data.get("tasks", {}),
            items=data.get("items", {}),
            state=data.get("state", {}),
        )

    def to_dict(self):
        """
        Converts :class:`Item <okami.api.Stats>` object into dictionary representation

        :returns: (dictionary)
        """
        return dict(
            times=self.times or {},
            tasks=self.tasks or {},
            items=self.items or {},
            state=self.state or {},
        )


class State:
    """
    :class:`State <okami.api.State>` object

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
    :class:`Task <okami.Task>` object

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
        Creates :class:`Task <okami.Task>` object from dictionary 'data'

        :param data: (dictionary)
        :returns: :class:`Task <okami.Task>` object
        """
        return cls(
            url=data["url"],
            data=data.get("data"),
        )

    def to_dict(self):
        """
        Converts :class:`Task <okami.Task>` object into dictionary representation

        :returns: (dictionary)
        """
        return dict(
            url=self.url,
            data=self.data,
        )


class Throttle:
    """
    :class:`Throttle <okami.Throttle>` object

    :param sleep: (float) sleep time between requests
    :param max_rps: (float) maximum number of requests per second
    :param fn: (function) custom function for calculating sleep time

    :ivar time_started: (float) time at start
    :ivar time_last_modified: (float) time at last request
    :ivar state: :class:`State <okami.api.State>` object
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

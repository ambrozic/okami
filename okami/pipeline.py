import aiohttp

from okami.configuration import settings


class Pipeline:
    """
    Base :class:`Pipeline <okami.pipeline.Pipeline>` object

    :param controller: :class:`Controller <okami.engine.Controller>` object
    """

    def __init__(self, controller):
        self.controller = controller

    async def process(self, something):
        """
        Processes passed object. Exceptions should be caught otherwise entire pipeline terminates.

        :param something: an object
        :returns: altered passed object
        """
        raise NotImplementedError


class Cache(Pipeline):
    async def process(self, spider):
        return spider


class Cleaner(Pipeline):
    async def process(self, items):
        return items


class ContentType(Pipeline):
    async def process(self, response):
        return response


class Headers(Pipeline):
    """
    :class:`Headers <okami.pipeline.Headers>` pipeline object
    """

    async def process(self, request):
        """
        Processes passed :class:`Request <okami.api.Request>` object.
        Exceptions should be caught otherwise entire pipeline terminates.

        :param request: :class:`Request <okami.api.Request>` object
        :returns: altered passed :class:`Request <okami.api.Request>` object
        """
        if not request.headers:
            request.headers.update(
                {
                    "User-Agent": settings.USER_AGENT,
                }
            )
        return request


class Images(Pipeline):
    async def process(self, items):
        for item in items:
            for image in item.images:
                pass
        return items


class Parser(Pipeline):
    async def process(self, items):
        return items


class Report(Pipeline):
    async def process(self, stats):
        print(
            "\033[94mOkami\033[0m:"
            "\033[91m{}\033[0m: "
            "delta=\033[92m{:.4f}\033[0m "
            "sleep=\033[92m{:.4f}\033[0m "
            "time=\033[92m{:.4f}\033[0m "
            "rps=\033[92m{:<6.2f}\033[0m "
            "i=\033[92m{}\033[0m - "
            "\033[96m{}\033[0m/\033[92m{}\033[0m/\033[91m{}\033[0m/\033[94m{}\033[0m - \033[96m{:.2f}s\033[0m".format(
                "leader" if self.controller.is_leader else "member",
                stats.state.get("delta", 0),
                stats.state.get("sleep", 0),
                stats.state.get("time", 0),
                stats.state.get("rps", 0),
                stats.state.get("iterations", 0),
                stats.tasks.get("queued", 0),
                stats.tasks.get("processed", 0),
                stats.tasks.get("failed", 0),
                stats.items.get("processed", 0),
                stats.times.get("running", 0),
            )
        )
        return stats


class Responses(Pipeline):
    async def process(self, response):
        return response


class Session(Pipeline):
    """
    :class:`Session <okami.pipeline.Session>` pipeline object
    """

    async def process(self, request):
        """
        Processes passed :class:`Request <okami.api.Request>` object.
        Exceptions should be caught otherwise entire pipeline terminates.

        :param request: :class:`Request <okami.api.Request>` object
        :returns: altered passed :class:`Request <okami.api.Request>` object
        """
        if not self.controller.session or self.controller.session.closed:
            try:
                self.controller.session = self.controller.spider.session()
            except NotImplementedError:
                connector = aiohttp.TCPConnector(
                    limit=settings.CONN_MAX_CONCURRENT_CONNECTIONS,
                    verify_ssl=settings.CONN_VERIFY_SSL,
                )
                self.controller.session = aiohttp.ClientSession(connector=connector)
        return request


class Settings(Pipeline):
    async def process(self, spider):
        return spider


class Tasks(Pipeline):
    async def process(self, tasks):
        return tasks

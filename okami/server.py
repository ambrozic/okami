import json
import logging
from urllib.parse import parse_qsl

import aiohttp
from aiohttp import web
from multidict import MultiDict

from okami import loader, settings
from okami.api import Task
from okami.engine import Controller

log = logging.getLogger(__name__)


class Server:
    def __init__(self, address):
        self.name = "Okami API Server"
        self.address = address
        self.app = web.Application(debug=settings.DEBUG)
        self.app.router.add_routes(
            [
                web.get(path="/", handler=self.view_index, name="index"),
                web.get(path="/process/", handler=self.view_process, name="process"),
            ]
        )
        self.controllers = dict()

    def start(self):
        host, port = self.address.split(":")
        print("{} at http://{}:{}".format(self.name, host, port))
        web.run_app(app=self.app, host=host, port=port, print=None)

    async def view_index(self, request):
        return web.Response(text="{} - {}".format(self.name, aiohttp.http.SERVER_SOFTWARE))

    async def view_process(self, request):
        params = MultiDict(parse_qsl(request.query_string))
        name = params.get("name")
        url = params.get("url")
        if name not in self.controllers:
            spider = loader.get_spider_class_by_name(name=name)()
            self.controllers[name] = Controller(spider=spider)
        controller = self.controllers[name]
        result = await controller.process(Task(url=url))
        items = [item.to_dict() for item in result.items]
        return web.Response(
            text=json.dumps(items, sort_keys=True, indent=4, separators=(",", ": ")),
            content_type="application/json",
        )

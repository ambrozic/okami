import asyncio
import json
import logging
from urllib.parse import parse_qsl

import aiohttp
from aiohttp import MultiDict, web

from okami import loader
from okami.api import Task
from okami.configuration import settings
from okami.engine import Controller

log = logging.getLogger(__name__)


class Server:
    def __init__(self, address):
        try:
            self.loop = None
            self.address = address.split(":")
            self.app = web.Application(debug=settings.DEBUG)
            self.app.router.add_route("GET", "/", self.view_index)
            self.app.router.add_route("GET", "/process/", self.view_process)
            self.controllers = dict()
        except Exception as e:
            log.exception(e)

    def start(self):
        handler = None
        server = None

        try:
            self.loop = asyncio.get_event_loop()
            self.loop.set_debug(enabled=settings.DEBUG)
            self.loop.slow_callback_duration = 0.2

            handler = self.app.make_handler()
            server = self.loop.run_until_complete(self.loop.create_server(handler, *self.address))
            log.debug("Okami HTTP Server started - {}:{}".format(*self.address))
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            log.exception(e)
        finally:
            self.loop.run_until_complete(handler.finish_connections(1.0))
            if server:
                server.close()
                self.loop.run_until_complete(server.wait_closed())
                self.loop.run_until_complete(self.app.cleanup())
            for controller in self.controllers.values():
                controller.close()
            if self.loop:
                self.loop.close()
            log.debug("Okami HTTP Server finished")

    async def view_index(self, request):
        return web.Response(text="Okami Server - {}".format(aiohttp.HttpMessage.SERVER_SOFTWARE))

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
            content_type="application/json"
        )

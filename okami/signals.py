import asyncio
import logging
import threading
import weakref

log = logging.getLogger(__name__)


class Signal:
    def __init__(self):
        self.receivers = []
        self.is_dirty = False
        self.lock = threading.Lock()

    def connect(self, receiver, **kwargs):
        obj = receiver
        receiver = weakref.ref(receiver)
        weakref.finalize(obj, self.flag)
        self.receivers.append(receiver)
        self.clear()

    def disconnect(self, receiver):
        try:
            self.receivers.remove(receiver)
        except ValueError:
            log.exception("%s receiver does not exist", receiver)
        self.clear()

    async def send(self, sender, **kwargs):
        for receiver in self.receivers:
            await receiver()(signal=self, sender=sender, **kwargs)

    def clear(self):
        if self.is_dirty and self.receivers:
            with self.lock:
                self.is_dirty = False
                cleared = []
                for receiver in self.receivers:
                    if receiver() is None:
                        continue
                    cleared.append(receiver)
                self.receivers = cleared

    def flag(self):
        self.is_dirty = True


def receiver(signal):
    def decorate(func):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("'{}' is not coroutine function".format(func.__name__))
        signal.connect(func)
        return func

    return decorate


http_middleware_initialised = Signal()
http_middleware_started = Signal()
http_middleware_finished = Signal()
http_middleware_finalised = Signal()

spider_middleware_initialised = Signal()
spider_middleware_started = Signal()
spider_middleware_finished = Signal()
spider_middleware_finalised = Signal()

response_created = Signal()

startup_pipeline_initialised = Signal()
startup_pipeline_started = Signal()
startup_pipeline_finished = Signal()
startup_pipeline_finalised = Signal()

items_pipeline_initialised = Signal()
items_pipeline_started = Signal()
items_pipeline_finished = Signal()
items_pipeline_finalised = Signal()

tasks_pipeline_initialised = Signal()
tasks_pipeline_started = Signal()
tasks_pipeline_finished = Signal()
tasks_pipeline_finalised = Signal()

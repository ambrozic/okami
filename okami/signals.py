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
            self.receivers.pop(receiver)  # eventually change to self.receivers.discard(receiver)
        except KeyError as e:
            log.exception("{} does not exist".format(receiver), e)
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


#: response object created
response_created = Signal()

#: http middleware started
http_middleware_started = Signal()
#: http middleware finished
http_middleware_finished = Signal()

#: startup pipeline started
startup_pipeline_started = Signal()
#: startup pipeline finished
startup_pipeline_finished = Signal()

#: stats pipeline started
stats_pipeline_started = Signal()
#: stats pipeline finished
stats_pipeline_finished = Signal()

#: requests pipeline started
requests_pipeline_started = Signal()
#: requests pipeline finished
requests_pipeline_finished = Signal()

#: responses pipeline started
responses_pipeline_started = Signal()
#: responses pipeline finished
responses_pipeline_finished = Signal()

#: items pipeline started
items_pipeline_started = Signal()
#: items pipeline finished
items_pipeline_finished = Signal()

#: tasks pipeline started
tasks_pipeline_started = Signal()
#: tasks pipeline finished
tasks_pipeline_finished = Signal()

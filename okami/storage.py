import queue
import time


class BaseStorage:
    """
    Base BaseStorage <okami.storage.BaseStorage>

    :param name: Spider <okami.Spider> name attribute
    """

    def __init__(self, name, **kwargs):
        self.name = name

    def to_dict(self):
        return dict()

    def finalise(self):
        pass

    def get_info_time_started(self):
        raise NotImplementedError

    def set_info_time_started(self, value):
        raise NotImplementedError

    def get_info_time_running(self):
        raise NotImplementedError

    def get_info_items_processed(self):
        raise NotImplementedError

    def add_info_items_processed(self, value):
        raise NotImplementedError

    def get_info_items_failed(self):
        raise NotImplementedError

    def add_info_items_failed(self, value):
        raise NotImplementedError

    def get_tasks_queued(self):
        raise NotImplementedError

    def add_tasks_queued(self, values):
        raise NotImplementedError

    def tasks_queued_is_empty(self):
        raise NotImplementedError

    def get_tasks_processed(self):
        raise NotImplementedError

    def add_tasks_processed(self, values):
        raise NotImplementedError

    def get_tasks_failed(self):
        raise NotImplementedError

    def add_tasks_failed(self, values):
        raise NotImplementedError


class Storage(BaseStorage):
    """
    Storage <okami.storage.Storage>

    :param name: Spider <okami.Spider> name attribute
    """

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.name = name
        self._info_time_started = None
        self._info_items_processed = 0
        self._info_items_failed = 0
        self._tasks_queued = queue.Queue()
        self._tasks_processed = set()
        self._tasks_failed = set()

    def to_dict(self):
        return dict(
            times_running=self.get_info_time_running(),
            tasks_queued=self._tasks_queued.qsize(),
            tasks_processed=len(self._tasks_processed),
            tasks_failed=len(self._tasks_failed),
            items_processed=self._info_items_processed,
            items_failed=self._info_items_failed,
        )

    def get_info_time_started(self):
        return self._info_time_started

    def set_info_time_started(self, value: float):
        self._info_time_started = float(value)

    def get_info_time_running(self):
        return (time.time() - self._info_time_started) if self._info_time_started else 0.0

    def get_info_items_processed(self):
        return self._info_items_processed

    def add_info_items_processed(self, value: int):
        self._info_items_processed += int(value)
        return self._info_items_processed

    def get_info_items_failed(self):
        return self._info_items_failed

    def add_info_items_failed(self, value: int):
        self._info_items_failed += int(value)
        return self._info_items_failed

    def add_tasks_queued(self, values: set):
        if not isinstance(values, set):
            raise ValueError
        values -= self._tasks_processed
        self.add_tasks_processed(values=values)
        for v in values:
            self._tasks_queued.put(item=v, timeout=0)

    def tasks_queued_is_empty(self):
        return self._tasks_queued.empty()

    def get_tasks_queued(self):
        return self._tasks_queued.get(timeout=0)

    def get_tasks_processed(self):
        return self._tasks_processed

    def add_tasks_processed(self, values: set):
        if not isinstance(values, set):
            raise ValueError
        self._tasks_processed |= values

    def get_tasks_failed(self):
        return self._tasks_failed

    def add_tasks_failed(self, values: set):
        if not isinstance(values, set):
            raise ValueError
        self._tasks_failed |= values

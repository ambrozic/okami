import pickle
import queue
import time

try:
    import redis
except ImportError:
    pass


class Storage(object):
    """
    Base :class:`Pipeline <okami.pipeline.Pipeline>` object

    :param name: :class:`Spider <okami.Spider>` object **name** attribute
    """

    def __init__(self, name, **kwargs):
        self.name = name

    def to_dict(self):
        return dict()

    def initialise(self):
        return False

    def finalise(self):
        pass

    def get_info_time_initialised(self):
        raise NotImplementedError

    def set_info_time_initialised(self, value):
        return NotImplementedError

    def get_info_time_started(self):
        raise NotImplementedError

    def set_info_time_started(self, value):
        raise NotImplementedError

    def get_info_time_running(self):
        raise NotImplementedError

    def get_info_time_initialising(self):
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


class LocalStorage(Storage):
    """
    :class:`Pipeline <okami.pipeline.Pipeline>` object

    :param name: :class:`Spider <okami.Spider>` object **name** attribute
    """

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.name = name
        self._info_time_initialised = None
        self._info_time_started = None
        self._info_items_processed = 0
        self._info_items_failed = 0
        self._tasks_queued = queue.Queue()
        self._tasks_processed = set()
        self._tasks_failed = set()

    def to_dict(self):
        return dict(
            times=dict(
                running=self.get_info_time_running()
            ),
            tasks=dict(
                queued=self._tasks_queued.qsize(),
                processed=len(self._tasks_processed),
                failed=len(self._tasks_failed),
            ),
            items=dict(
                processed=self._info_items_processed,
                failed=self._info_items_failed,
            )
        )

    def initialise(self):
        return True

    def get_info_time_initialised(self):
        return self._info_time_initialised

    def set_info_time_initialised(self, value: float):
        self._info_time_initialised = float(value)

    def get_info_time_started(self):
        return self._info_time_started

    def set_info_time_started(self, value: float):
        self._info_time_started = float(value)

    def get_info_time_running(self):
        return (time.time() - self._info_time_started) if self._info_time_started else 0.0

    def get_info_time_initialising(self):
        return (self._info_time_started or 0.0) - (self._info_time_initialised or 0.0)

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
            self._tasks_queued.put(item=v, timeout=0.1)

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


class RedisStorage(Storage):
    """
    :class:`Pipeline <okami.pipeline.Pipeline>` object

    :param name: :class:`Spider <okami.Spider>` object **name** attribute
    :param url: in a form like *redis://localhost:6379/0*
    """

    def __init__(self, name, url, **kwargs):
        super().__init__(name, **kwargs)
        self.name = name
        self.url = url
        self.pool = None
        self.max_connections = kwargs.get("max_connections", 50)
        self.codec = pickle

    @property
    def db(self):
        if not self.pool:
            self.pool = redis.ConnectionPool.from_url(url=self.url, max_connections=self.max_connections)
        return redis.StrictRedis(connection_pool=self.pool)

    def to_dict(self):
        return dict(
            times=dict(
                running=self.get_info_time_running()
            ),
            tasks=dict(
                queued=int(self.db.llen("{}:tasks:queued".format(self.name))),
                processed=int(self.db.scard("{}:tasks:processed".format(self.name))),
                failed=int(self.db.scard("{}:tasks:failed".format(self.name))),
            ),
            items=dict(
                processed=self.get_info_items_processed(),
                failed=self.get_info_items_failed(),
            )
        )

    def initialise(self):
        initialised = self.db.setnx("{}:leader".format(self.name), 1)
        keys = self.db.keys("{}:*:*".format(self.name))
        if keys:
            self.db.delete(*keys)
        return initialised

    def finalise(self):
        self.db.delete("{}:leader".format(self.name))
        self.pool.disconnect()

    def get_info_time_initialised(self):
        key = "{}:info:time_initialised".format(self.name)
        time_initialised = self.db.get(key)
        return float(time_initialised) if time_initialised else None

    def set_info_time_initialised(self, value: float):
        if not isinstance(value, float):
            raise ValueError
        key = "{}:info:time_initialised".format(self.name)
        self.db.set(key, float(value))

    def get_info_time_started(self):
        key = "{}:info:time_started".format(self.name)
        time_started = self.db.get(key)
        return float(time_started) if time_started else None

    def set_info_time_started(self, value: float):
        if not isinstance(value, float):
            raise ValueError
        key = "{}:info:time_started".format(self.name)
        self.db.set(key, float(value))

    def get_info_time_running(self):
        time_started = self.get_info_time_started()
        return (time.time() - time_started) if time_started else 0

    def get_info_time_initialising(self):
        time_initialising = self.get_info_time_initialising()
        return (time.time() - time_initialising) if time_initialising else 0

    def get_info_items_processed(self):
        key = "{}:info:items_processed".format(self.name)
        processed = self.db.get(key)
        return int(processed) if processed else 0

    def add_info_items_processed(self, value: int):
        if not isinstance(value, (float, int)):
            raise ValueError
        key = "{}:info:items_processed".format(self.name)
        return int(self.db.incr(key, int(value)))

    def get_info_items_failed(self):
        key = "{}:info:items_failed".format(self.name)
        failed = self.db.get(key)
        return int(failed) if failed else 0

    def add_info_items_failed(self, value: int):
        if not isinstance(value, (float, int)):
            raise ValueError
        key = "{}:info:items_failed".format(self.name)
        return int(self.db.incr(key, int(value)))

    def filter(self, values: set):
        if not isinstance(values, set):
            raise ValueError
        if values:
            key = "{}:tasks:processed".format(self.name)
            lua = """
                local results = {}
                for _, e in pairs(ARGV) do
                    local x = redis.call('sismember', KEYS[1], e)
                    if x == 1 then
                        table.insert(results, e)
                    end
                end
                return results
            """
            script = self.db.register_script(lua)
            results = script(keys=[key], args={self.codec.dumps(v) for v in values})
            return values - {self.codec.loads(e) for e in results}

    def add_tasks_queued(self, values: set):
        if not isinstance(values, set):
            raise ValueError
        values = self.filter(values=values)
        self.add_tasks_processed(values=values)
        key = "{}:tasks:queued".format(self.name)
        if values:
            self.db.rpush(key, *{self.codec.dumps(v) for v in values})

    def get_tasks_queued(self):
        key = "{}:tasks:queued".format(self.name)
        e = self.db.blpop(key, timeout=1)
        if e:
            return self.codec.loads(e[1])
        raise queue.Empty

    def tasks_queued_is_empty(self):
        key = "{}:tasks:queued".format(self.name)
        return self.db.llen(key) == 0

    def get_tasks_processed(self):
        key = "{}:tasks:processed".format(self.name)
        return {self.codec.loads(e) for e in self.db.smembers(key)}

    def add_tasks_processed(self, values):
        if not isinstance(values, set):
            raise ValueError
        if values:
            key = "{}:tasks:processed".format(self.name)
            self.db.sadd(key, *{self.codec.dumps(v) for v in values})

    def get_tasks_failed(self):
        key = "{}:tasks:failed".format(self.name)
        return {self.codec.loads(e) for e in self.db.smembers(key)}

    def add_tasks_failed(self, values):
        if not isinstance(values, set):
            raise ValueError
        if values:
            key = "{}:tasks:failed".format(self.name)
            self.db.sadd(key, *{self.codec.dumps(v) for v in values})

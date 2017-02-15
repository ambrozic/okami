from okami import constants

# Okami settings module name
OKAMI_SETTINGS = None

#: Debugging
DEBUG = False

#: List of python packages containing spider implementations
SPIDERS = []

#: Storage class name
STORAGE = "okami.storage.LocalStorage"

#: Downloader class name
DOWNLOADER = "okami.Downloader"

#: HTTP server class name
HTTP_SERVER = "okami.server.Server"

#: Throttle class name
THROTTLE = "okami.Throttle"

#: Arguments passed to storage module
STORAGE_SETTINGS = {}

#: Arguments passed to throttle module
THROTTLE_SETTINGS = {}

#: HTTP server default address
HTTP_SERVER_ADDRESS = "0.0.0.0:5566"

#: Default USER-AGENT used in requests
USER_AGENT = "Okami/{}.{}".format(*constants.VERSION)

#: Set a custom event loop policy
EVENT_LOOP_POLICY = None

#: Asyncio Future object timeout, https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.wait
ASYNC_TIMEOUT = 10

#: Pause timeout, in case of server connection errors etc. okami pauses scrapping
PAUSE_TIMEOUT = 5

#: Connection timeout
CONN_TIMEOUT = 20

#: SSL verification for HTTP requests
CONN_VERIFY_SSL = False

#: Maximum number of concurrent connections to website
CONN_MAX_CONCURRENT_CONNECTIONS = 5

#: Maximum number of concurrent requests to website. Effectively this is async loop size.
CONN_MAX_CONCURRENT_REQUESTS = 10

#: Maximum number of connection retries in case of connection issues
CONN_MAX_RETRIES = 5

#: Maximum number of HTTP redirects
CONN_MAX_HTTP_REDIRECTS = 10

#: Maximum number of failed requests before okami stops
REQUEST_MAX_FAILED = 50

#: Maximum number of pending requests before logging an error
REQUEST_MAX_PENDING = 10

#: List of base http middleware. Should not change.
BASE_HTTP_MIDDLEWARE = ()

#: List of http middleware. Use to add custom handlers.
HTTP_MIDDLEWARE = ()

#: List of base startup pipelines. Should not change.
BASE_STARTUP_PIPELINE = ()

#: List of base stats pipelines. Should not change.
BASE_STATS_PIPELINE = ()

#: List of base requests pipelines. Should not change.
BASE_REQUESTS_PIPELINE = (
    "okami.pipeline.Session",
    "okami.pipeline.Headers",
)

#: List of base responses pipelines. Should not change.
BASE_RESPONSES_PIPELINE = ()

#: List of base items pipelines. Should not change.
BASE_ITEMS_PIPELINE = ()

#: List of base tasks pipelines. Should not change.
BASE_TASKS_PIPELINE = ()

#: List of startup pipelines. Use to add custom handlers.
STARTUP_PIPELINE = ()

#: List of stats pipelines. Use to add custom handlers.
STATS_PIPELINE = ()

#: Frequency rate for running stats pipelines.
STATS_PIPELINE_FREQUENCY = 100

#: List of requests pipelines. Use to add custom handlers.
REQUESTS_PIPELINE = ()

#: List of responses pipelines. Use to add custom handlers.
RESPONSES_PIPELINE = ()

#: List of items pipelines. Use to add custom handlers.
ITEMS_PIPELINE = ()

#: List of tasks pipelines. Use to add custom handlers.
TASKS_PIPELINE = ()

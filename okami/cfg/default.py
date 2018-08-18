import okami

# Okami version
VERSION = okami.__version__

# Enable debugging for asyncio module
DEBUG = False

# List of python modules in your project containing spider implementations available to okami
SPIDERS = []

# Storage class path and name
STORAGE = "okami.Storage"

# Downloader class path and name
DOWNLOADER = "okami.Downloader"

# HTTP server class path and name
HTTP_SERVER = "okami.server.Server"

# Throttle class path and name
THROTTLE = "okami.Throttle"

# Arguments passed to storage module
STORAGE_SETTINGS = {}

# Arguments passed to throttle module
THROTTLE_SETTINGS = {}

# HTTP server default address
HTTP_SERVER_ADDRESS = "0.0.0.0:5566"

# Default USER-AGENT used in requests
USER_AGENT = "Okami/{}".format(okami.__version__)

# Set a custom event loop policy object
# Details: https://docs.python.org/3/library/asyncio-eventloops.html#customizing-the-event-loop-policy.
EVENT_LOOP_POLICY = None

# Asyncio Future object timeout
# Details: https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.wait
ASYNC_TIMEOUT = 10

# Asyncio minimum duration in seconds of slow callbacks
# Details: https://docs.python.org/3/library/asyncio-dev.html#asyncio-debug-mode
ASYNC_SLOW_CALLBACK_DURATION = 0.1

# Pause timeout, in case of server connection errors etc. okami pauses scraping
PAUSE_TIMEOUT = 5

# Connection timeout
CONN_TIMEOUT = 20

# SSL verification for HTTP requests
CONN_VERIFY_SSL = False

# Maximum number of concurrent connections to website
CONN_MAX_CONCURRENT_CONNECTIONS = 5

# Maximum number of concurrent requests to website. Effectively an async loop size.
CONN_MAX_CONCURRENT_REQUESTS = 10

# Maximum number of connection retries in case of connection issues
CONN_MAX_RETRIES = 5

# Maximum number of HTTP redirects
CONN_MAX_HTTP_REDIRECTS = 10

# Maximum number of failed requests before okami stops
REQUEST_MAX_FAILED = 50

# Maximum number of pending requests before logging an error
REQUEST_MAX_PENDING = 10

# List of base http middleware. Should not change.
BASE_HTTP_MIDDLEWARE = (
    "okami.middleware.Session",
    "okami.middleware.Headers",
)

# List of http middleware. Use to add custom handlers.
HTTP_MIDDLEWARE = ()

# List of base spider middleware. Should not change.
BASE_SPIDER_MIDDLEWARE = ()

# List of spider middleware. Use to add custom handlers.
SPIDER_MIDDLEWARE = ()

# List of base startup pipelines. Should not change.
BASE_STARTUP_PIPELINE = ()

# List of startup pipelines. Use to add custom handlers.
STARTUP_PIPELINE = ()

# List of base items pipelines. Should not change.
BASE_ITEMS_PIPELINE = ()

# List of items pipelines. Use to add custom handlers.
ITEMS_PIPELINE = ()

# List of base tasks pipelines. Should not change.
BASE_TASKS_PIPELINE = ()

# List of tasks pipelines. Use to add custom handlers.
TASKS_PIPELINE = ()

# Delta middleware enable
DELTA_ENABLED = False

# Delta middleware database directory. Defaults to current directory.
DELTA_PATH = None

# Settings

Settings can be defined as **OKAMI_SETTINGS** environment variable otherwise default settings will be loaded.

It should be set like this

- `export OKAMI_SETTINGS=okami.cfg.example`

or passed with command

- `OKAMI_SETTINGS=okami.cfg.example okami command`

To import okami settings in your project use this `from okami import settings`.


####
Below are available okami settings located in `okami.cfg.default` module with default values.


&nbsp;
#### VERSION
Current okami version 

&nbsp;
#### DEBUG
Enable debugging for asyncio module. Check [Debug mode of asyncio](https://docs.python.org/3/library/asyncio-dev.html#asyncio-debug-mode) documentation. 

==default==`DEBUG = False`

&nbsp;
#### SPIDERS
List of python modules in your project containing spider implementations available to okami.

==default==`SPIDERS = []`

&nbsp;
#### STORAGE 
Storage class path and name

==default==`STORAGE = "okami.Storage"`

&nbsp;
#### DOWNLOADER
Downloader class path and name

==default==`DOWNLOADER = "okami.Downloader"`

&nbsp;
#### HTTP_SERVER
HTTP server class path and name

==default==`HTTP_SERVER = "okami.server.Server"`

&nbsp;
#### THROTTLE
Throttle class path and name

==default==`THROTTLE = "okami.Throttle"`

&nbsp;
#### STORAGE_SETTINGS
Arguments passed to storage module

==default==`STORAGE_SETTINGS = {}`

&nbsp;
#### THROTTLE_SETTINGS
Arguments passed to throttle module

==default==`THROTTLE_SETTINGS = {}`

&nbsp;
#### HTTP_SERVER_ADDRESS
HTTP server default address

==default==`HTTP_SERVER_ADDRESS = "0.0.0.0:5566"`

&nbsp;
#### USER_AGENT
Default USER-AGENT used in requests

==default==`USER_AGENT = "Okami/{}".format(okami.__version__)`

&nbsp;
#### EVENT_LOOP_POLICY
Set a custom event loop policy object. Check [Customizing the event loop policy](https://docs.python.org/3/library/asyncio-eventloops.html#customizing-the-event-loop-policy) documentation.

==default==`EVENT_LOOP_POLICY = None`

&nbsp;
#### ASYNC_TIMEOUT
Asyncio Future object timeout. Check [concurrent.futures.wait](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.wait) documentation.

==default==`ASYNC_TIMEOUT = 10`

&nbsp;
#### ASYNC_SLOW_CALLBACK_DURATION
Asyncio minimum duration in seconds of slow callbacks. Check [Debug mode of asyncio](https://docs.python.org/3/library/asyncio-dev.html#asyncio-debug-mode) documentation.

==default==`ASYNC_SLOW_CALLBACK_DURATION = 0.1`

&nbsp;
#### PAUSE_TIMEOUT 
Pause timeout, in case of server connection errors etc. okami pauses scraping

==default==`PAUSE_TIMEOUT = 5`

&nbsp;
#### CONN_TIMEOUT
Connection timeout

==default==`CONN_TIMEOUT = 20`

&nbsp;
#### CONN_VERIFY_SSL
SSL verification for HTTP requests

==default==`CONN_VERIFY_SSL = False`

&nbsp;
#### CONN_MAX_CONCURRENT_CONNECTIONS 
Maximum number of concurrent connections to website

==default==`CONN_MAX_CONCURRENT_CONNECTIONS = 5`

&nbsp;
#### CONN_MAX_CONCURRENT_REQUESTS
Maximum number of concurrent requests to website. Effectively an async loop size.

==default==`CONN_MAX_CONCURRENT_REQUESTS = 10`

&nbsp;
#### CONN_MAX_RETRIES
Maximum number of connection retries in case of connection issues

==default==`CONN_MAX_RETRIES = 5`

&nbsp;
#### CONN_MAX_HTTP_REDIRECTS 
Maximum number of HTTP redirects

==default==`CONN_MAX_HTTP_REDIRECTS = 10`

&nbsp;
#### REQUEST_MAX_FAILED
Maximum number of failed requests before okami stops

==default==`REQUEST_MAX_FAILED = 50`

&nbsp;
#### REQUEST_MAX_PENDING
Maximum number of pending requests before logging an error

==default==`REQUEST_MAX_PENDING = 10`

&nbsp;
#### BASE_HTTP_MIDDLEWARE 
List of base http middleware. Should not change.

==default==
```
BASE_HTTP_MIDDLEWARE = (
    "okami.middleware.Session",
    "okami.middleware.Headers",
)
```

&nbsp;
#### HTTP_MIDDLEWARE 
List of http middleware. Use to add custom handlers.

==default==`HTTP_MIDDLEWARE = ()`

&nbsp;
#### BASE_SPIDER_MIDDLEWARE
List of base spider middleware. Should not change.

==default==`BASE_SPIDER_MIDDLEWARE = ()`

&nbsp;
#### SPIDER_MIDDLEWARE
List of spider middleware. Use to add custom handlers.

==default==`SPIDER_MIDDLEWARE = ()`

&nbsp;
#### BASE_STARTUP_PIPELINE 
List of base startup pipelines. Should not change.

==default==`BASE_STARTUP_PIPELINE = ()`

&nbsp;
#### STARTUP_PIPELINE 
List of startup pipelines. Use to add custom handlers.

==default==`STARTUP_PIPELINE = ()`

&nbsp;
#### BASE_ITEMS_PIPELINE 
List of base items pipelines. Should not change.

==default==`BASE_ITEMS_PIPELINE = ()`

&nbsp;
#### ITEMS_PIPELINE 
List of items pipelines. Use to add custom handlers.

==default==`ITEMS_PIPELINE = ()`

&nbsp;
#### BASE_TASKS_PIPELINE 
List of base tasks pipelines. Should not change.

==default==`BASE_TASKS_PIPELINE = ()`

&nbsp;
#### TASKS_PIPELINE 
List of tasks pipelines. Use to add custom handlers.

==default==`TASKS_PIPELINE = ()`

&nbsp;
#### DELTA_ENABLED
Delta middleware enable

==default==`DELTA_ENABLED = False`

&nbsp;
#### DELTA_PATH 
Delta middleware database directory. Defaults to current directory.

==default==`DELTA_PATH = None`

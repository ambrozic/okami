DEBUG = False
SPIDERS = ["okami"]
CONN_MAX_CONCURRENT_REQUESTS = 50
REQUEST_MAX_FAILED = 200
REQUEST_MAX_PENDING = 200
TASKS_PIPELINE = (
    "okami.pipeline.Tasks",
)
ITEMS_PIPELINE = (
    "okami.pipeline.Cleaner",
    "okami.pipeline.Parser",
    "okami.pipeline.Images",
)
RESPONSES_PIPELINE = (
    "okami.pipeline.Responses",
    "okami.pipeline.ContentType",
)
STARTUP_PIPELINE = (
    "okami.pipeline.Settings",
    "okami.pipeline.Cache",
)
HTTP_MIDDLEWARE = (
    "okami.middleware.TestMiddleware",
)

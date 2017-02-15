DEBUG = True
SPIDERS = ["okami"]
THROTTLE_SETTINGS = dict(max_rps=500)
STATS_PIPELINE_FREQUENCY = 1
STATS_PIPELINE = (
    "okami.pipeline.Report",
)
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

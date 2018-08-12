DEBUG = False
SPIDERS = ["okami"]
THROTTLE_SETTINGS = dict(max_rps=500)
TASKS_PIPELINE = (
    "okami.pipeline.Tasks",
)
ITEMS_PIPELINE = (
    "okami.pipeline.Cleaner",
    "okami.pipeline.Parser",
    "okami.pipeline.Images",
)
STARTUP_PIPELINE = (
    "okami.pipeline.Settings",
    "okami.pipeline.Cache",
)
HTTP_MIDDLEWARE = (
    "okami.middleware.Logger",
)
SPIDER_MIDDLEWARE = (
    "okami.middleware.Delta",
)

# Middlewares

Middleware is a recursive or two-way chain of processing elements. Input object is processed in a forward way and passed between middlewares and used to generate a result. Result is then processed backward and passed between middlewares in reverse order into final output object.

Exceptions during middleware exceptions are important. Every middleware can raise an exception which terminates entire chain. If this is not a desirable option, middleware should catch and log or ignore exceptions.

Okami runs several middlewares during spider initialisation and page processing cycle. There are several built-in middlewares and you can define your own middlewares.

For a more visual representation on how middlewares are involved in processing cycle, check [schema](architecture.md#schema) on architecture page.


## Http middleware

Http middleware wraps request/response and downloader cycle and runs for every page. Middlewares are defined as a tuple in [settings](settings.md) as [BASE_HTTP_MIDDLEWARE](settings.md#base_http_middleware) and [HTTP_MIDDLEWARE](settings.md#http_middleware) and merged into a single tuple. First are executed *BASE_HTTP_MIDDLEWARE*, following are custom ones defined in *HTTP_MIDDLEWARE*.

All phases involved in http middleware are described below.

### Initialise

Executes middleware `initialise` method at the beginning of scraping process when okami starts.

### Before

During before phase, middleware elements are executed in same order as defined in a tuple and are passed [Request](api.md#request) object. HttpMiddleware `before` method is called to process [Request](api.md#request) object.

Final [Request](api.md#request) object is used by [Downloader](api.md#downloader) to create a [Response](api.md#response) object.

### After

[Response](api.md#response) is passed in after phase to middleware elements executed now in reverse order as defined in tuple. HttpMiddleware `after` method is called to process passed objects.

Final [Response](api.md#response) object is then used for actual data processing.

### Finalise

Executes http middleware `finalise` method at the end of scraping process just before okami terminates.


## Spider middleware

Spider middleware wraps spider cycle and runs for every page. Middlewares are defined as a tuple in [settings](settings.md) as [BASE_SPIDER_MIDDLEWARE](settings.md#base_spider_middleware) and [SPIDER_MIDDLEWARE](settings.md#SPIDER_MIDDLEWARE) and merged into a single tuple. First are executed *BASE_SPIDER_MIDDLEWARE*, following are custom ones defined in *SPIDER_MIDDLEWARE*.

All phases involved in spider middleware are described below.

### Initialise

Executes middleware `initialise` method at the beginning of scraping process when okami starts.

### Before

During before phase, middleware elements are executed in same order as defined in a tuple and are passed [Task](api.md#task), [Response](api.md#response) object. SpiderMiddleware `before` method is called to process [Response](api.md#response) object.

Final [Request](api.md#request) object is used by [Spider](api.md#spider) to create a list of [Task](api.md#task) and a list of [Item](api.md#item) objects.

### After

[Task](api.md#task), [Response](api.md#response), a list of [Task](api.md#task) and a list of [Item](api.md#item) objects are passed in after phase to middleware elements executed now in reverse order as defined in tuple. SpiderMiddleware `after` is method called to process passed object.

Final passed objects are then used in further request/response and downloader cycle as well as in `TasksPipeline <okami.engine.TasksPipeline>` and `ItemsPipeline <okami.engine.ItemsPipeline>`.

### Finalise

Executes spider middleware `finalise` method at the end of scraping process just before okami terminates.

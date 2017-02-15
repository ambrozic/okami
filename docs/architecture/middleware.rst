.. _architecture-middleware:

Middleware
==========

Middleware is a recursive or two-way chain of processing elements. Input is processed in a forward way and used to generate a result. Result is then processed backward into an output.

An example is :class:`HttpMiddleware <okami.engine.HttpMiddleware>`. Elements are defined as a tuple in :ref:`settings <usage-settings#defaults>`. **BASE_HTTP_MIDDLEWARE** and **HTTP_MIDDLEWARE** are merged into single tuple. First are executed **BASE_HTTP_MIDDLEWARE**, following are custom ones defined in **HTTP_MIDDLEWARE**.

|

**Input phase**

During input phase, middleware elements are executed in same order as defined in a tuple and are passed :class:`Request <okami.api.Request>` object. **Middleware.before** method is called to process :class:`Request <okami.api.Request>` object.

Final :class:`Request <okami.api.Request>` object is used by :class:`Downloader <okami.Downloader>` to create a :class:`Response <okami.api.Response>` object.

|

**Output phase**

:class:`Response <okami.api.Response>` is passed in output phase to middleware elements executed now in reverse order as defined in tuple. **Middleware.after** method called to process :class:`Response <okami.api.Response>` object.

Final :class:`Response <okami.api.Response>` object is then used for actual data processing.

|

Exceptions during middleware execution are important. Every middleware can raise an exception which terminates entire chain. If this is not a desirable option, middleware should silently catch and log or ignore exceptions.

|

.. _architecture-middleware#available:

Available Middleware
--------------------

.. autoclass:: okami.engine.HttpMiddleware
    :members:
.. automodule:: okami.configuration.default
    :members: HTTP_MIDDLEWARE
    :noindex:

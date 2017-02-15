.. _architecture-spiders:

Spiders
=======

Spiders are the business end of Okami. Their main function is to provide URL parsing rules and web page content parsing for a particular web site.

Spiders are fed :class:`Response <okami.api.Response>` object processed by :ref:`Responses Pipelines <usage-pipelines#responses>`. :class:`Response <okami.api.Response>` object contains complete HTTP response.

Spiders, if needed, also handle authentication and session for HTTP negotiation with website.

Process
-------

- Okami starts processing website at URLs defined in *Spider.urls.start* dictionary

- URL for every page is passed through :ref:`Requests Pipelines <usage-pipelines#requests>` into :ref:`Downloader <architecture-downloader>` where page is downloaded and :class:`Response <okami.api.Response>` object created

- :class:`Response <okami.api.Response>` object is passed through :ref:`Responses Pipelines <usage-pipelines#responses>` and processed if necessary

- :class:`Response <okami.api.Response>` object is further processed using *Spider.urls.allow* and *Spider.urls.avoid* rules to get a list of URLs. Visited URLs are ignored, non-visited URLs are queued

- Same :class:`Response <okami.api.Response>` object is passed into :class:`Spider.items <okami.Spider>` method where page content is processed and a list of Item objects is created

- Item objects are passed into :ref:`Items Pipelines <usage-pipelines#items>` for further processing, cleanup, storage in database etc.

Same process is repeated for every single valid URL. Once URLs are exhausted, Okami terminates.

|

.. autoclass:: okami.api.BaseSpider
    :members:

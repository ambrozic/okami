.. _usage-spiders:

Spiders
=======

|

.. _usage-spiders#requirements:

Notes
-----

- Spiders should have unique class property **name**.

- Keep your spiders in a python package. You can have multiple packages. Define them in :ref:`settings <usage-settings>`.

 - *SPIDERS=["path.to.package.spiders"]*

- Okami finds and loads spiders from this packages using property **name**.

|

.. _usage-spiders#development:

Development
-----------

Make sure everything is properly configured. During development you can test run your spider using command below:

 - ``okami process spider_name url``

This will run a spider with name **spider_name** against page at **url**. Output should be a *JSON* representation of a list of *Item* objects.

|

.. _usage-spiders#details:

Details
-------
Below are required and optional implementation details for every spider.

|

**Required**

- **Spider.urls** dictionary defines rules used by Okami to parse a list of valid URLs from page content for further website processing.

    -  **Spider.name** - required and it should be unique

    -  **Spider.urls.start** - URLs used as starting URLs for processing website

    -  **Spider.urls.allow** - Allowed URLs for further website processing

    -  **Spider.urls.avoid** - URLs that are avoided during website processing

- :class:`Spider.items <okami.Spider.items>` method receives :class:`Task <okami.Task>` object, processes page content and returns a list of :class:`Item <okami.Item>` objects.

- :class:`Spider.tasks <okami.Spider.tasks>` method receives :class:`Task <okami.Task>` object, processes page content and returns a list of :class:`Task <okami.Task>` objects with **urls** and optionally **data** for further processing.

|

**Optional**

    - :class:`Spider.session <okami.Spider.session>` method is optionally used to handle authentication etc.

    - :class:`Spider.request <okami.Spider.request>` method is optionally used to define a dictionary of extra arguments passed into :class:`Request <okami.api.Request>` object used by :ref:`Downloader <architecture-downloader>` to create an HTTP request and download a page

|

.. _usage-spiders#example:

Example
-------

Below is an example :class:`Spider <okami.Spider>` implementation.

.. literalinclude:: ../../okami/example.py
    :language: python
    :linenos:
    :pyobject: Example

|

And an example :class:`Item <okami.Item>` implementation.

.. literalinclude:: ../../okami/example.py
    :language: python
    :linenos:
    :pyobject: Product

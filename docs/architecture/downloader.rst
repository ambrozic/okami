.. _architecture-downloader:

Downloader
==========

|

Receives a :class:`Request <okami.api.Request>` object from a :ref:`Requests Pipelines <usage-pipelines#requests>` and creates an HTTP request to a page. HTTP response is processed into a :class:`Response <okami.api.Response>` object, passed into :ref:`Responses Pipelines <usage-pipelines#responses>` and further into a spider for parsing.

Override
--------
Use **DOWNLOADER** from :ref:`settings <usage-settings#defaults>` when you need to define a custom downloader functionality.

|

.. autoclass:: okami.api.Downloader

.. literalinclude:: ../../okami/api.py
    :language: python
    :pyobject: Downloader
    :linenos:

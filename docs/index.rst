.. _index:

Okami
-----

|

Okami is a high-level web scraping framework built entirely in Python 3.5+ using asynchronous model provided by standard library `asyncio <https://docs.python.org/3/library/asyncio.html>`_ module with `aiohttp <http://aiohttp.readthedocs.org/>`_ as a networking layer and `lxml <http://lxml.de/>`_ for parsing data.

:ref:`Architecture <architecture>` is entirely modular and main components can be swapped out and replaced with custom implementations..

**Features**

- complete website-wide page processing
- immediate, on-demand or real-time page processing over HTTP API
- single page processing via command line

Okami can be deployed as a single application process per processing website or in a cluster of multiple instances processing same website. In this case, `redis <https://redis.io>`_ is used as a storage.

:ref:`Spiders <usage-spiders#example>` are very simple implementations. `lxml.xpath <http://lxml.de/>`_ is used for parsing data.

|

Usage
-----

This part of the documentation will give most information on how to start and use Okami.

.. toctree::
    :maxdepth: 2

    usage/index

|

Architecture
------------

This part of the documentation explains technical details of Okami architecture.

.. toctree::
    :maxdepth: 2

    architecture/index

|

Community
---------

This part of the documentation explains how to contribute to Okami project.

.. toctree::
    :maxdepth: 2

    community

|

License
-------
Okami is licensed under a three clause BSD License.

Full license text can be found :ref:`here <license>`.

.. toctree::
    :hidden:

    license

|

Release Notes
-------------

.. toctree::
    :maxdepth: 2

    changes

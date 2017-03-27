Okami
=====

.. image:: https://readthedocs.org/projects/okami/badge/?version=latest
    :target: http://okami.readthedocs.io/

.. image:: https://img.shields.io/pypi/v/okami.svg
    :target: https://pypi.python.org/pypi/okami

.. image:: https://img.shields.io/pypi/l/okami.svg
    :target: https://pypi.python.org/pypi/okami

.. image:: https://img.shields.io/pypi/wheel/okami.svg
    :target: https://pypi.python.org/pypi/okami

.. image:: https://img.shields.io/pypi/pyversions/okami.svg
    :target: https://pypi.python.org/pypi/okami

.. image:: https://travis-ci.org/ambrozic/okami.svg?branch=master
    :target: https://travis-ci.org/ambrozic/okami

.. image:: https://codecov.io/github/ambrozic/okami/coverage.svg?branch=master
    :target: https://codecov.io/github/ambrozic/okami

|

Okami is a high-level web scraping framework built entirely in Python 3.5+ using asynchronous model provided by standard library `asyncio <https://docs.python.org/3/library/asyncio.html>`_ module with `aiohttp <http://aiohttp.readthedocs.org/>`_ as a networking layer and `lxml <http://lxml.de/>`_ for parsing data.

Architecture is entirely modular and main components can be swapped out and replaced with custom implementations.

**Features**

- complete website-wide page processing
- immediate, on-demand or real-time page processing over HTTP API
- single page processing via command line

Okami can be deployed as a single application process per processing website or in a cluster of multiple instances processing same website. In this case, `redis <https://redis.io>`_ is used as a storage.

Spiders are very simple implementations. `lxml.xpath <http://lxml.de/>`_ is used for parsing data.

|

Quick start
-----------

- Install okami

  - ``pip install okami``

- Run example web server

  - ``OKAMI_SETTINGS=okami.configuration.example okami example server``

Open http://localhost:8000/ and browse around a little. Quite a remarkable website. We will run our example spider against this website shortly and process few items.

|

- Run example spider

  - ``OKAMI_SETTINGS=okami.configuration.example okami example spider``

Our example spider started and you can monitor it processing pages. Take a look at example spider implementation `here </ambrozic/okami/blob/master/okami/example.py#L15>`_.

|

Documentation
-------------

Read rest of documentation on `okami.readthedocs.org <http://okami.readthedocs.org>`_

|

License
-------
Okami is licensed under a three clause BSD License.

Full license text can be found `here <license>`_.

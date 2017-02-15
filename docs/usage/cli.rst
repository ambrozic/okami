.. _usage-cli:

CLI
===
Command line interface

|

**OKAMI_SETTINGS** environment variable should always be set

``export OKAMI_SETTINGS=path.to.your.settings``

or set environment variable inline before okami command

``OKAMI_SETTINGS=path.to.your.settings okami command``

|

.. _usage-cli#application:

Application
-----------
Run Okami application for **spider_name**

``okami start spider_name``

|

.. _usage-cli#server:

Server
------
Start Okami server.

- ``okami server``

Access Okami server at **settings.HTTP_SERVER_ADDRESS** or `localhost:8000 <http://localhost:5566/>`_

Try an API HTTP call to Okami server for **example.com** spider.

.. code-block:: bash

    $ http 'http://localhost:5566/process/?name=example.com&url=http://localhost:8000/men-backpacks/142000/'

    HTTP/1.1 200 OK
    CONNECTION: keep-alive
    CONTENT-LENGTH: 799
    CONTENT-TYPE: application/json; charset=utf-8
    DATE: Tue, 22 Dec 2015 18:06:10 GMT
    SERVER: Python/3.5 aiohttp/0.19.0

    [
        {
            "category": "men-backpacks",
            "desc": "some desc 142000",
            "iid": 142000,
            "images": [
                "http://localhost:8000/images/name-4/4.png",
                "http://localhost:8000/images/name-5/5.png",
                "http://localhost:8000/images/name-6/6.png",
                "http://localhost:8000/images/name-7/7.png",
                "http://localhost:8000/images/name-8/8.png",
                "http://localhost:8000/images/name-9/9.png",
                "http://localhost:8000/images/name-10/10.png",
                "http://localhost:8000/images/name-11/11.png",
                "http://localhost:8000/images/name-12/12.png"
            ],
            "name": "name 142000",
            "price": 933.43,
            "url": "http://localhost:8000/men-backpacks/142000/"
        }
    ]

|

.. _usage-cli#process:

Process
-------
Process a single **url** for **spider_name** from command line.

- ``okami process spider_name url``

.. code-block:: bash

    $ okami process example.com http://localhost:8000/men-backpacks/142000/
    [
        {
            "category": "men-backpacks",
            "desc": "some desc 142000",
            "iid": 142000,
            "images": [
                "http://localhost:8000/images/name-4/4.png",
                "http://localhost:8000/images/name-5/5.png",
                "http://localhost:8000/images/name-6/6.png",
                "http://localhost:8000/images/name-7/7.png",
                "http://localhost:8000/images/name-8/8.png",
                "http://localhost:8000/images/name-9/9.png",
                "http://localhost:8000/images/name-10/10.png",
                "http://localhost:8000/images/name-11/11.png",
                "http://localhost:8000/images/name-12/12.png"
            ],
            "name": "name 142000",
            "price": 995.89,
            "url": "http://localhost:8000/men-backpacks/142000/"
        }
    ]

|

.. _usage-cli#example:

Example
-------
For running example use default settings.

- ``export OKAMI_SETTINGS=okami.configuration.default``

Run example web server.

- ``okami example server``

Run example spider. It will run against example web server and process some data.

- ``okami example spider``

|

.. _usage-cli#list:

List
----
Lists available spiders

- ``okami list``

|

.. _usage-cli#profile:

Profile
-------
Profile application or spiders during development. Its using ``cProfile``. Optionally result can be exported into a file and used for more detailed analysis or visualisations.

- ``okami profile spider_name``

.. code-block:: bash

    $ okami profile example.com --limit=0.01 --sort=tottime --strip

    Settings:
        OKAMI_SETTINGS: okami.configuration.test
        DEBUG: False
        SPIDERS: ['okami']
        STORAGE: okami.storage.LocalStorage
        STORAGE_SETTINGS: {}
        CONN_MAX_CONCURRENT_REQUESTS: 50
        REQUEST_MAX_FAILED: 200
        REQUEST_MAX_PENDING: 200
        THROTTLE: okami.api.Throttle
        THROTTLE_SETTINGS: {}

    Results:
        3607600 function calls (3598126 primitive calls) in 10.085 seconds

    Ordered by: internal time
    List reduced from 886 to 18 due to restriction <0.02>

    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
      4536    3.673    0.001    3.673    0.001 {method 'control' of 'select.kqueue' objects}
      4458    1.184    0.000    1.195    0.000 __init__.py:759(document_fromstring)
      2229    0.760    0.000    2.224    0.001 spider.py:70(tasks)
    207217    0.400    0.000    0.400    0.000 {method 'match' of '_sre.SRE_Pattern' objects}
      2229    0.386    0.000    0.970    0.000 example.py:34(items)
        39    0.158    0.004    0.158    0.004 {built-in method builtins.compile}
      4504    0.148    0.000   10.053    0.002 base_events.py:1216(_run_once)
     13374    0.140    0.000    0.140    0.000 {method 'search' of '_sre.SRE_Pattern' objects}
      2230    0.128    0.000    0.198    0.000 storage.py:151(add_tasks_queued)
      2229    0.120    0.000    3.390    0.002 spider.py:41(process)
      2229    0.092    0.000    0.154    0.000 spider.py:84(<setcomp>)
    100260    0.091    0.000    0.552    0.000 utils.py:22(parse_domain_url)
    128747    0.078    0.000    0.113    0.000 __init__.py:736(lookup)
    105101    0.066    0.000    0.066    0.000 {method 'format' of 'str' objects}
    299700    0.065    0.000    0.130    0.000 {built-in method builtins.isinstance}
      2229    0.056    0.000    0.083    0.000 protocol.py:65(parse_headers)
      4483    0.055    0.000    1.227    0.000 client.py:99(_request)
      4458    0.055    0.000    0.607    0.000 spider.py:81(<setcomp>)

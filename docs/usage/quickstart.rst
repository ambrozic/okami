.. _usage-quickstart:

Quick start
===========

|

We will try to run example web server and spider. Spider will process items from example web server.

.. _usage-quickstart#install:

Install
-------
``pip install okami``

|

.. _quickstart#settings:

Settings
--------
Use default **OKAMI_SETTINGS**

``export OKAMI_SETTINGS=okami.configuration.example``

|

.. _quickstart#server:

Server
------
Run example web server

``okami example server``

Open `localhost:8000 <http://localhost:8000/>`_ and browse around a little. Quite a remarkable website. We will run our example spider against this website shortly and process few items.

|

.. _quickstart#spider:

Spider
------
Run example spider

``okami example spider``

Our example spider starts and you can monitor it processing pages. Take a look at example spider implementation :ref:`here <usage-spiders#example>`.

|

.. _quickstart#project:

Project
-------
To create a new project you will need the following:

- create python module for :ref:`settings <usage-settings>`

- create a package with your :ref:`spiders <usage-spiders>` and define it in settings

 - *SPIDERS=["path.to.package.spiders"]*

|

That is all for now. Try and run your spider by executing in shell:

``OKAMI_SETTINGS=path.to.your.settings okami start spider_name``


Your spider should be running. Next step should be to check default :ref:`settings <usage-settings#defaults>`, maybe set up your first pipelines and start collecting some data.

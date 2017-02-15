.. _usage-server:

Server
======

|

.. _usage-server#run:

Run
---

- ``okami server``

Access Okami server at **settings.HTTP_SERVER_ADDRESS** or `localhost:5566 <http://localhost:5566/>`_

.. _usage-server#endpoints:

Endpoints
---------

**/process/**

- method

  - GET

- parameters

  - **name** *spider name*

  - **url** *page url*

- example

 - http://localhost:5566/process/?name=example.com&url=http://example.com/men-backpacks/142000/

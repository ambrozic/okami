.. _usage-api:

API
===

This part of the documentation is raw Okami API documentation.

|

Main
----

.. autoclass:: okami.Spider
   :inherited-members:

|

.. autoclass:: okami.Item
   :inherited-members:

|

.. autoclass:: okami.Task
   :inherited-members:

|

.. autoclass:: okami.api.Request
   :inherited-members:

|

.. autoclass:: okami.api.Response
   :inherited-members:

|

.. autoclass:: okami.api.Stats
   :inherited-members:

|

Components
----------

.. autoclass:: okami.Downloader
   :inherited-members:

|

.. autoclass:: okami.api.Result
   :inherited-members:

|

.. autoclass:: okami.api.State
   :inherited-members:

|

.. autoclass:: okami.Throttle
   :inherited-members:

|


Pipelines
---------

.. autoclass:: okami.pipeline.Pipeline
   :inherited-members:

|

.. autoclass:: okami.pipeline.Headers
   :inherited-members:

|

.. autoclass:: okami.pipeline.Session
   :inherited-members:

|

Engine
------

.. autoclass:: okami.engine.Okami
  :inherited-members:
.. autoclass:: okami.engine.Manager
  :inherited-members:
.. autoclass:: okami.engine.Controller
  :inherited-members:

|

Storage
-------

.. autoclass:: okami.storage.Storage
  :inherited-members:
.. autoclass:: okami.storage.LocalStorage
  :inherited-members:
.. autoclass:: okami.storage.RedisStorage
  :inherited-members:

|

Constants
---------

.. autoclass:: okami.constants.status
  :members:
.. autoclass:: okami.constants.method
  :members:

|


Exceptions
----------

.. autoexception:: okami.exceptions.OkamiException
.. autoexception:: okami.exceptions.OkamiTerminationException
.. autoexception:: okami.exceptions.NoSuchSpiderException
.. autoexception:: okami.exceptions.SpiderException
.. autoexception:: okami.exceptions.PipelineException
.. autoexception:: okami.exceptions.StartupPipelineException
.. autoexception:: okami.exceptions.StatsPipelineException
.. autoexception:: okami.exceptions.RequestsPipelineException
.. autoexception:: okami.exceptions.ResponsesPipelineException
.. autoexception:: okami.exceptions.ItemsPipelineException

.. _architecture-pipelines:

Pipelines
=========

|

    *In software engineering, a pipeline consists of a chain of processing elements (processes, threads, coroutines, functions, etc.), arranged so that the output of each element is the input of the next; the name is by analogy to a physical pipeline.*

    -- `WikiPedia <https://en.wikipedia.org/wiki/Pipeline_(software)>`_

|

Each pipeline chain runs at different frequency. Some only once i.e. at startup, most of them are called on each request and some follow frequency settings.

Pipelines are executed in same order as they are defined in :ref:`settings <usage-settings#defaults>`. First executed are base pipelines following are custom ones.

Each pipeline in a pipeline chain is passed same object. Object can be changed by each pipeline and a final version of passed object is returned by pipeline chain.

Exceptions during pipeline are important. Every pipeline can raise an exception which terminates entire pipeline chain. If this is not a desirable option, pipelines should silently catch and log or ignore exceptions.

|

.. _architecture-pipelines#available:

Available Pipelines
-------------------

.. autoclass:: okami.engine.StartupPipelines
    :members:
.. automodule:: okami.configuration.default
    :members: STARTUP_PIPELINE
    :noindex:

|

.. autoclass:: okami.engine.StatsPipelines
    :members:
.. automodule:: okami.configuration.default
    :members: STATS_PIPELINE, STATS_PIPELINE_FREQUENCY
    :noindex:

|

.. autoclass:: okami.engine.RequestsPipelines
    :members:
.. automodule:: okami.configuration.default
    :members: REQUESTS_PIPELINE
    :noindex:

|

.. autoclass:: okami.engine.ResponsesPipelines
    :members:
.. automodule:: okami.configuration.default
    :members: RESPONSES_PIPELINE
    :noindex:

|

.. autoclass:: okami.engine.ItemsPipelines
    :members:
.. automodule:: okami.configuration.default
    :members: ITEMS_PIPELINE
    :noindex:

|

.. autoclass:: okami.engine.TasksPipelines
    :members:
.. automodule:: okami.configuration.default
    :members: TASKS_PIPELINE
    :noindex:

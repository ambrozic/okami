.. _usage-signals:

Signals
=======

|

Okami includes a **signal dispatcher** to enable implementations get notified when actions occur elsewhere in the platform. Signals allow **senders** to notify a multiple **receivers** about certain actions or events.

|

.. _usage-signals#receiving-signals:

Receiving signals
-----------------
In code example below, function **request_created** connects to signal **signals.signal_request_created** by being decorated with **signals.receiver**.

Function **request_created** will be called every time signal **signals.signal_request_created** is executed.

.. code-block:: python

    from okami import signals

    @signals.receiver(signals.signal_request_created)
    async def request_created(signal, sender, **kwargs):
        print("request_created: {}, {}, {}".format(signal, sender, kwargs))

|

.. _usage-signals#available-signals:

Available signals
-----------------
Okami provides a set of built-in signals.

.. autodata:: okami.signals.items_pipeline_started
.. autodata:: okami.signals.items_pipeline_finished
.. autodata:: okami.signals.response_created
.. autodata:: okami.signals.responses_pipeline_started
.. autodata:: okami.signals.responses_pipeline_finished
.. autodata:: okami.signals.requests_pipeline_started
.. autodata:: okami.signals.requests_pipeline_finished
.. autodata:: okami.signals.startup_pipeline_started
.. autodata:: okami.signals.startup_pipeline_finished
.. autodata:: okami.signals.stats_pipeline_started
.. autodata:: okami.signals.stats_pipeline_finished
.. autodata:: okami.signals.tasks_pipeline_started
.. autodata:: okami.signals.tasks_pipeline_finished

|

.. _usage-signals#configuration:

Configuration
-------------
Make sure your signal receivers are imported at some point in your project otherwise add

``from your.app import signals``

somewhere, i.e. in your top **__init__.py** module.

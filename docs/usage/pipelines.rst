.. _usage-pipelines:

Pipelines
=========

|

    *In software engineering, a pipeline consists of a chain of processing elements (processes, threads, coroutines, functions, etc.), arranged so that the output of each element is the input of the next; the name is by analogy to a physical pipeline.*

    -- `WikiPedia <https://en.wikipedia.org/wiki/Pipeline_(software)>`_

|

Okami runs several pipelines during spider initialisation and page processing cycle. There are several built-in pipelines but you can define your own pipelines.

For a more visual representation on how pipelines are involved in processing cycle, check :ref:`schema <architecture#schema>` on :ref:`architecture <architecture>` page or read more into details about pipelines :ref:`here <architecture-pipelines>`.


|

.. _usage-pipelines#startup:

Startup
-------
Startup pipeline runs once when spider is initialised.

**STARTUP_PIPELINE** tuple from :ref:`settings <usage-settings#defaults>` defines a list of custom startup pipelines. Tuple order of pipelines is preserved during execution.

|

.. _usage-pipelines#stats:

Stats
-----
Stats pipeline runs once every 100 requests.

**STATS_PIPELINE** tuple from :ref:`settings <usage-settings#defaults>` defines a list of custom stats pipelines. Tuple order of pipelines is preserved during execution.

|

.. _usage-pipelines#requests:

Requests
--------
Requests pipeline runs for every **url** before processing actual page at **url**. Pipeline is processing a :class:`Request <okami.api.Request>` object which is going to be used for HTTP request of a page.

**REQUESTS_PIPELINE** tuple from :ref:`settings <usage-settings#defaults>` defines a list of custom requests pipelines. Tuple order of pipelines is preserved during execution.

|

.. _usage-pipelines#responses:

Responses
---------
Responses pipeline runs every time after page at **url** is processed. Pipeline is processing a :class:`Response <okami.api.Response>` object returned after HTTP request of a page.

**RESPONSES_PIPELINE** tuple from :ref:`settings <usage-settings#defaults>` defines a list of custom responses pipelines. Tuple order of pipelines is preserved during execution.

|

.. _usage-pipelines#items:

Items
-----
Items pipeline runs every time after page at **url** is processed. Pipeline is processing a list of :class:`Item <okami.Item>` objects.

**ITEMS_PIPELINE** tuple from :ref:`settings <usage-settings#defaults>` defines a list of custom items pipelines. Tuple order of pipelines is preserved during execution.

|

.. _usage-pipelines#tasks:

Tasks
-----
Tasks pipeline runs every time after page at **url** is processed. Pipeline is processing a list of :class:`Task <okami.Task>` objects used for queuing nad further processing.

**TASKS_PIPELINE** tuple from :ref:`settings <usage-settings#defaults>` defines a list of custom tasks pipelines. Tuple order of pipelines is preserved during execution.

|

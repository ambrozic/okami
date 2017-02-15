.. _usage-middleware:

Middleware
==========
For a more visual representation on how middleware is involved in processing cycle, check :ref:`schema <architecture#schema>` on :ref:`architecture <architecture>` page or read more into details about middleware :ref:`here <architecture-middleware>`.

|

.. _usage-middleware#http:

HTTP Middleware
---------------
HTTP middleware runs every single time during request/response phase.

**HTTP_MIDDLEWARE** tuple from :ref:`settings <usage-settings#defaults>` defines a list of custom http middleware. Tuple order is preserved during execution.

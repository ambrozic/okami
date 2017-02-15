.. _architecture-storage:

Storage
=======

|

Okami needs to keep internal state. Storage module is used as an API.

Available storage APIs:
    - :class:`okami.storage.LocalStorage <okami.storage.LocalStorage>`
    - :class:`okami.storage.RedisStorage <okami.storage.RedisStorage>`

By default, :class:`okami.storage.LocalStorage <okami.storage.LocalStorage>` is used. When running in cluster mode, :class:`okami.storage.RedisStorage <okami.storage.RedisStorage>` should be configured.

Override
--------
Use **STORAGE** from :ref:`settings <usage-settings#defaults>` when you need to define a custom storage functionality.

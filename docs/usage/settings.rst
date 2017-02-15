.. _usage-settings:

Settings
========

|

Settings module is defined as an environmental variable **OKAMI_SETTINGS** pointing to a python module with your settings.

- ``OKAMI_SETTINGS=path.to.your.settings``.

Okami first loads ``okami.configuration.default`` module and applies values from your settings module on top.

|

.. _usage-settings#usage:

Usage
-----
To import setting in your project use

``from okami.configuration import settings``

|

.. _usage-settings#defaults:

Defaults
--------

|

.. automodule:: okami.configuration.default
    :members:
    :member-order: bysource

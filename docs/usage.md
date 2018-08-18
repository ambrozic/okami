We will try to run example web server and spider. Spider will process items from example web server.

## Install

`pip install okami`


## Settings

Use example **OKAMI_SETTINGS**

`export OKAMI_SETTINGS=okami.cfg.example`


## Server

Run example web server

`okami example server`

Open [localhost:8000](http://localhost:8000/) and browse around a little. Quite a remarkable website. We will run our example spider against this website shortly and process few items.


## Spider

Run example spider

`okami example spider`

Our example spider started and you can see it is processing pages. Take a look at an example spider implementation [here](https://github.com/ambrozic/okami/blob/master/okami/example.py#L14-L53).


## Project

To create a new project you will need the following:

- create python module for [settings](docs/settings.md) to be used as **OKAMI_SETTINGS** environment variable
    - `OKAMI_SETTINGS=okami.cfg.example`

- create a module with your spiders and define it as **SPIDERS** in [settings](docs/settings.md#spiders) module

    - `SPIDERS=["path.to.package.spiders"]`

That is all for now. Try and run your spider by executing following command in shell:

`OKAMI_SETTINGS=path.to.your.settings okami start spider-name`

Your spider should be running. Next step should be to check default [settings](docs/settings.md), maybe set up your first [pipeline](docs/pipelines.md) or [middleware](docs/middlewares.md) and start collecting some data.

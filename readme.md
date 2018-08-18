# Okami

[![](https://img.shields.io/badge/docs-github-blue.svg)](https://ambrozic.github.io/okami)
[![](https://img.shields.io/pypi/pyversions/okami.svg)](https://pypi.python.org/pypi/okami)
[![](https://img.shields.io/pypi/v/okami.svg)](https://pypi.python.org/pypi/okami)
[![](https://img.shields.io/pypi/wheel/okami.svg)](https://pypi.python.org/pypi/okami)
[![](https://travis-ci.org/ambrozic/okami.svg?branch=master)](https://travis-ci.org/ambrozic/okami)
[![](https://codecov.io/github/ambrozic/okami/coverage.svg?branch=master)](https://codecov.io/github/ambrozic/okami)
[![](https://img.shields.io/pypi/l/okami.svg)](https://pypi.python.org/pypi/okami)

Okami is a high-level web scraping framework built entirely for Python 3.6+ using asynchronous model provided by standard library [asyncio](https://docs.python.org/3/library/asyncio.html) module with [aiohttp](https://docs.aiohttp.org) as a networking layer and [lxml](http://lxml.de) for parsing data.

Architecture is entirely modular and main components can be swapped out and replaced with custom implementations.

## Features

- complete website-wide page processing
- full scraping mode or delta mode scraping only unvisited pages
- immediate, on-demand or real-time page processing over HTTP API
- single page processing via command line
- lots of pipelines, middlewares and signals

Spiders are very simple implementations. Take a look at an example [here](https://github.com/ambrozic/okami/blob/master/okami/example.py#L14-L53).


## Quick start

- Install okami

  - `pip install okami`

- Run example web server

  - `OKAMI_SETTINGS=okami.cfg.example okami example server`

Open [localhost:8000](http://localhost:8000) and browse around a little. Quite a remarkable website. We will run our example spider against this website shortly and process few items.

- Run example spider

  - `OKAMI_SETTINGS=okami.cfg.example okami example spider`

Our example spider started and you can see it processing pages. Take a look at an example spider implementation [here](https://github.com/ambrozic/okami/blob/master/okami/example.py#L14-L53).


## Documentation

Read the rest of documentation [here](https://ambrozic.github.io/okami).


## License

Okami is licensed under a three clause BSD License. Full license text can be found [here](https://github.com/ambrozic/okami/blob/master/license).

# Introduction

Okami is a high-level web scraping framework built entirely for Python 3.6+ using asynchronous model provided by standard library [asyncio](https://docs.python.org/3/library/asyncio.html) module with [aiohttp](https://docs.aiohttp.org) as a networking layer and [lxml](http://lxml.de) for parsing data.

Architecture is entirely modular and main components can be swapped out and replaced with custom implementations.


## Features

- complete website-wide page processing
- full scraping mode or delta mode scraping only unvisited pages
- immediate, on-demand or real-time page processing over HTTP API
- single page processing via command line
- lots of pipelines, middlewares and signals

Spiders are very simple implementations. Take a look at an example [here](https://github.com/ambrozic/okami/blob/master/okami/example.py#L14-L53) or continue to [usage](usage.md) documentation page.


## License

Okami is licensed under a three clause BSD License. Full license text can be found [here](license.md).

# CLI
This page of the documentation will explain okami command line interface or CLI.


## Options
- `-h / --help` print help or more information about each command
- `-V / --version` print okami version
- `-s / --setup` install okami bash completion


## Commands

### Start
==command==`okami start spider-name`

Runs okami application for a spider.
```
$ okami start spider-name
Okami: spider-name - delta=0.0001 sleep=0.0001 time=0.0002 rps=0.00   i=0 - 0/1/0/0 - 0.02s
Okami: spider-name - delta=0.0001 sleep=0.0001 time=0.0002 rps=0.00   i=1 - 43/45/0/0 - 0.03s
Okami: spider-name - delta=0.0108 sleep=0.0000 time=0.0109 rps=91.35  i=2 - 90/93/0/0 - 0.04s
...
```


### List
==command==`okami list`

Lists available spiders in project.
```
$ okami list

Spiders (3)
  spider1  okami.spider1:spider1
  spider2  okami.spider2:spider2
  spider3  okami.spider2:spider3
```


### Server
==command==`okami server`

Starts okami [server](server.md). Server, by default, can be accessed at [localhost:5566](http://localhost:5566). 

Use [HTTP_SERVER_ADDRESS](settings.md#http_server_address) or command line arguments to define custom address and port.
```
$ okami server
Okami API Server at http://0.0.0.0:5566
```

Try an API HTTP call to okami server for `example.com` spider. Both `okami server` and `okami example server` should be running.
```
$ http 'http://localhost:5566/process/?name=example.com&url=http://localhost:8000/men-backpacks/142000/'
HTTP/1.1 200 OK
Content-Length: 776
Content-Type: application/json; charset=utf-8
Date: Fri, 23 Dec 2016 00:00:00 GMT
Server: Python/3.6 aiohttp/3.3.2

[
    {
        "category": "men-backpacks",
        "desc": "some desc 142000",
        "iid": 142000,
        "images": [
            "http://localhost:8000/images/name-4/4.png",
            "http://localhost:8000/images/name-5/5.png",
            "http://localhost:8000/images/name-6/6.png",
            "http://localhost:8000/images/name-7/7.png",
            "http://localhost:8000/images/name-8/8.png",
            "http://localhost:8000/images/name-9/9.png",
            "http://localhost:8000/images/name-10/10.png",
            "http://localhost:8000/images/name-11/11.png",
            "http://localhost:8000/images/name-12/12.png"
        ],
        "name": "name 142000",
        "price": 48.85,
        "url": "http://localhost:8000/men-backpacks/142000/"
    }
]
```

### Process
==command==`okami process spider-name`

Process a single *url* for *spider-name* from command line. It is crucial during development of spiders to test page processing.
```
$ okami process example.com http://localhost:8000/women-belts/251000/
[
    {
        "category": "women-belts",
        "desc": "some desc 251000",
        "iid": 251000,
        "images": [
            "http://localhost:8000/images/name-4/4.png",
            "http://localhost:8000/images/name-5/5.png",
            "http://localhost:8000/images/name-6/6.png",
            "http://localhost:8000/images/name-7/7.png",
            "http://localhost:8000/images/name-8/8.png",
            "http://localhost:8000/images/name-9/9.png",
            "http://localhost:8000/images/name-10/10.png",
            "http://localhost:8000/images/name-11/11.png",
            "http://localhost:8000/images/name-12/12.png",
            "http://localhost:8000/images/name-13/13.png"
        ],
        "name": "name 251000",
        "price": 126.64,
        "url": "http://localhost:8000/women-belts/251000/"
    }
]
```


### Example

#### Server
==command==`okami example server`

Runs example web server.
```
$ okami example server
Okami Example Server at http://localhost:8000/ - items: 2184, delay: 0.0
```


#### Spider
==command==`okami example spider`

Runs example spider. It will run against example web server and process some data so make sure example server is running as well.
```
$ okami example spider
Okami: example.com - delta=0.0001 sleep=0.0001 time=0.0002 rps=0.00   i=0 - 0/1/0/0 - 0.02s
Okami: example.com - delta=0.0001 sleep=0.0001 time=0.0002 rps=0.00   i=1 - 43/45/0/0 - 0.03s
Okami: example.com - delta=0.0108 sleep=0.0000 time=0.0109 rps=91.35  i=2 - 90/93/0/0 - 0.04s
...
```


### Profile
==command==`okami server spider-name`

Profile application or spiders during development. It is using `cProfile`. Optionally, result can be exported into a file and used for more detailed analysis or visualisations.
```
$ okami profile example.com

  Settings:
    OKAMI_SETTINGS: okami.cfg.example
    LOOP: <_UnixSelectorEventLoop running=False closed=False debug=False>
    DEBUG: False
    SPIDERS: ['okami']
    STORAGE: okami.Storage
    STORAGE_SETTINGS: {}
    CONN_MAX_CONCURRENT_REQUESTS: 10
    REQUEST_MAX_FAILED: 50
    REQUEST_MAX_PENDING: 10
    THROTTLE: okami.Throttle
    THROTTLE_SETTINGS: {'max_rps': 500}
    DELTA_ENABLED: False

  Results:
         4477750 function calls (4472759 primitive calls) in 7.558 seconds

   Ordered by: cumulative time
   List reduced from 1159 to 232 due to restriction <0.2>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    7.561    7.561 okami/engine.py:23(start)
        1    0.000    0.000    7.559    7.559 asyncio/base_events.py:432(run_until_complete)
        1    0.011    0.011    7.559    7.559 asyncio/base_events.py:404(run_forever)
    15615    0.234    0.000    7.548    0.000 asyncio/base_events.py:1335(_run_once)
    15621    0.035    0.000    6.325    0.000 asyncio/events.py:143(_run)
     4462    0.044    0.000    5.883    0.001 okami/engine.py:96(process)
     2229    0.125    0.000    3.700    0.002 okami/api.py:43(process)
     2229    0.822    0.000    2.619    0.001 okami/api.py:72(tasks)
     4462    0.040    0.000    1.803    0.000 okami/api.py:99(process)
     4462    0.010    0.000    1.513    0.000 aiohttp/client.py:842(__aenter__)
     4462    0.094    0.000    1.502    0.000 aiohttp/client.py:222(_request)
     4458    1.075    0.000    1.086    0.000 lxml/html/__init__.py:759(document_fromstring)
     4458    0.149    0.000    1.008    0.000 okami/api.py:83(<setcomp>)
     2229    0.393    0.000    0.969    0.000 okami/example.py:32(items)
    15617    0.045    0.000    0.944    0.000 selectors.py:572(select)
    15623    0.885    0.000    0.885    0.000 {method 'control' of 'select.kqueue' objects}
   100260    0.087    0.000    0.538    0.000 okami/utils.py:23(parse_domain_url)
   204986    0.403    0.000    0.403    0.000 {method 'match' of '_sre.SRE_Pattern' objects}
   ...
```


### Shell
==command==`okami shell`

Just because. And it requires [IPython](https://ipython.org/) to be installed.
```
$ okami shell

     ██████╗ ██╗  ██╗ █████╗ ███╗   ███╗██╗
    ██╔═══██╗██║ ██╔╝██╔══██╗████╗ ████║██║
    ██║   ██║█████╔╝ ███████║██╔████╔██║██║
    ██║   ██║██╔═██╗ ██╔══██║██║╚██╔╝██║██║
    ╚██████╔╝██║  ██╗██║  ██║██║ ╚═╝ ██║██║
     ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝
    shell

Python 3.6.0 (default, Dec 23, 2016, 00:00:00)
Type 'copyright', 'credits' or 'license' for more information
IPython 6.5.0 -- An enhanced Interactive Python. Type '?' for help.
In [1]:
```

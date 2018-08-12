# Signals

Okami includes a signal dispatcher which allows applications to get notified when actions occur somewhere in okami framework. 

Signals allow certain senders to notify a set of receivers that some action has taken place. 

They’re especially useful when many pieces of code may be interested in the same events.


## Receiving signals

In code example below, function `response_created` connects to signal `signals.response_created` by being decorated with `signals.receiver`.

Function `response_created` will be called every time signal `signals.response_created` is executed.

```
from okami import signals

@signals.receiver(signals.response_created)
async def response_created(signal, sender, **kwargs):
    print("response_created: {}, {}, {}".format(signal, sender, kwargs))
```


## Configuration

Configuration is a bit awkward because of the way python decorators work.

Make sure your signal receivers are imported at some point in your project otherwise add

`from your.app import signals`

somewhere, i.e. in your top `__init__.py` module.



## Available signals

Okami provides a set of built-in signals.

### Http middleware signals
- http_middleware_initialised
- http_middleware_started
- http_middleware_finished
- http_middleware_finalised

### Spider middleware signals
- spider_middleware_initialised
- spider_middleware_started
- spider_middleware_finished
- spider_middleware_finalised

### Downloader signals
- response_created

### Startup pipeline signals
- startup_pipeline_initialised
- startup_pipeline_started
- startup_pipeline_finished
- startup_pipeline_finalised

### Items pipeline signals
- items_pipeline_initialised
- items_pipeline_started
- items_pipeline_finished
- items_pipeline_finalised

### Tasks pipeline signals
- tasks_pipeline_initialised
- tasks_pipeline_started
- tasks_pipeline_finished
- tasks_pipeline_finalised

# Pipelines

!!! quote ""
    In software engineering, a pipeline consists of a chain of processing elements (processes, threads, coroutines, functions, etc.), arranged so that the output of each element is the input of the next; the name is by analogy to a physical pipeline.
    
    – [WikiPedia](https://en.wikipedia.org/wiki/Pipeline_(software))


Each pipeline chain runs at a different frequency. Some only once i.e. at certain point in process, most are called after request is processed and some follow frequency settings.

Pipelines are executed in same order as they are defined in [settings](settings.md). First executed are base pipelines following are custom ones.

Each pipeline in a pipeline chain is passed same object. Object can be changed by each pipeline and a final version of passed object is returned by pipeline chain.

Exceptions during pipeline are important. Every pipeline can raise an exception which terminates entire pipeline chain. If this is not a desirable option, pipelines should silently catch and log or ignore exceptions.


Okami runs several pipelines during spider initialisation and page processing cycle. There are several built-in pipelines and you can define your own pipelines.

For a more visual representation on how pipelines are involved in processing cycle, check [schema](architecture.md#schema) on architecture page.


## Startup pipeline

Startup pipeline runs once when spider is initialised.

[STARTUP_PIPELINE](settings.md#startup_pipeline) tuple from [settings](settings.md) defines a list of custom startup pipelines. Tuple order of pipelines is preserved during execution.

All phases involved in startup pipeline are described below.

### Initialise

Executes pipeline `initialise` method at the beginning of scraping process when okami starts.

### Process

During process phase, pipeline `process` method is called to process [Spider](api.md#spider) object.

### Finalise

Executes startup pipeline `finalise` method at the end of scraping process just before okami terminates.


## Items pipeline

Items pipeline runs every time after page at url is processed. Pipeline is processing a list of [Item](api.md#item) objects returned by spider.

[ITEMS_PIPELINE](settings.md#items_pipeline) tuple from [settings](settings.md) defines a list of custom items pipelines. Tuple order of pipelines is preserved during execution.

All phases involved in items pipeline are described below.

### Initialise

Executes pipeline `initialise` method at the beginning of scraping process when okami starts.

### Process

During process phase, pipeline `process` method is called to process a set of [Item](api.md#item) objects.

### Finalise

Executes items pipeline `finalise` method at the end of scraping process just before okami terminates.


## Tasks pipeline

Tasks pipeline runs every time after page at url is processed. Pipeline is processing a list of [Task](api.md#task) objects returned by spider and used for queuing and further processing.

[TASKS_PIPELINE](settings.md#tasks_pipeline) tuple from [settings](settings.md) defines a list of custom tasks pipelines. Tuple order of pipelines is preserved during execution.

All phases involved in tasks pipeline are described below.

### Initialise

Executes pipeline `initialise` method at the beginning of scraping process when okami starts.

### Process

During process phase, pipeline `process` method is called to process a set of [Task](api.md#task) objects.

### Finalise

Executes tasks pipeline `finalise` method at the end of scraping process just before okami terminates.

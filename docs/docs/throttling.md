# Throttling


!!! quote ""
    In software, a throttling process, or a throttling controller as it is sometimes called, is a process responsible for regulating the rate at which application processing is conducted, either statically or dynamically.
    
    – [WikiPedia](https://en.wikipedia.org/wiki/Throttling_process_(computing))


Okami is controlling processing throughput using class [Throttle](api.md#throttle). [Throttle](api.md#throttle) keeps track of processed items and response times for every iteration using this values to calculate next iteration.

[Throttle](api.md#throttle) can control maximum RPS (requests per second) or sleep time directly for every iteration. It supports dynamic calculation for both of this values i.e. increasing or decreasing iteration sleep value based on responsiveness (page response time) of a website being processed.

## Customise

Use [THROTTLE_SETTINGS](settings.md#throttle_settings) from [settings](settings.md) module.

```python
# set fixed sleep time
THROTTLE_SETTINGS = dict(sleep=0.001)

# or set RPS limit
THROTTLE_SETTINGS = dict(max_rps=20)

# or use dynamic sleep time calculation
THROTTLE_SETTINGS = dict(fn=lambda state: 0.2 if state.delta > 2.0 else 0.001)
```

Function for custom control is passed a [State](api.md#state) object with current values. Returned value is a *float* object, a sleep time used in next iteration.

## Override

Override [THROTTLE](settings.md#throttle) class when you wish to define custom throttling functionality.

import weakref
from unittest import mock

import pytest

from okami import settings, signals, loader
from okami.engine import StartupPipeline
from okami.signals import Signal


def test_signal_connect():
    s = Signal()

    async def func(signal, sender, **kwargs):
        pass

    s.clear = mock.Mock()
    s.connect(func)
    assert s.receivers == [weakref.ref(func)]


def test_signal_disconnect():
    s = s = Signal()

    @signals.receiver(signal=s)
    async def func1(signal, sender, **kwargs):
        pass

    @signals.receiver(signal=s)
    async def func2(signal, sender, **kwargs):
        pass

    s.clear = mock.Mock()
    assert s.receivers == [weakref.ref(func1), weakref.ref(func2)]
    s.disconnect(weakref.ref(func1))
    assert s.clear.call_count == 1

    assert s.receivers == [weakref.ref(func2)]
    s.disconnect(weakref.ref(func2))
    assert s.clear.call_count == 2
    assert s.receivers == []

    # should catch ValueError
    s.disconnect(weakref.ref(func2))
    assert s.clear.call_count == 3


@pytest.mark.asyncio
async def test_signal_send(coro):
    s = Signal()

    result1 = mock.Mock()
    result2 = mock.Mock()
    sender = object()
    s.receivers = [mock.Mock(side_effect=[coro(result1)]), mock.Mock(side_effect=[coro(result2)])]
    await s.send(sender=sender, a=1, b=2)
    assert result1.call_count == 1
    assert result2.call_count == 1
    assert result1.call_args_list == [mock.call(a=1, b=2, sender=sender, signal=s)]
    assert result2.call_args_list == [mock.call(a=1, b=2, sender=sender, signal=s)]

    result1 = mock.Mock()
    s.receivers = [mock.Mock(side_effect=[coro(result1), coro(result1)])]
    await s.send(sender=sender, a=1, b=2)
    await s.send(sender=sender, a=1, b=2)
    assert result1.call_count == 2
    assert result1.call_args_list == [
        mock.call(a=1, b=2, sender=sender, signal=s), mock.call(a=1, b=2, sender=sender, signal=s),
    ]


def test_signal_clear():
    s = Signal()

    @signals.receiver(signal=s)
    async def func1(signal, sender, **kwargs):
        pass

    @signals.receiver(signal=s)
    async def func2(signal, sender, **kwargs):
        pass

    assert s.receivers == [weakref.ref(func1), weakref.ref(func2)]
    s.clear()
    assert s.is_dirty is False
    assert s.receivers == [weakref.ref(func1), weakref.ref(func2)]

    s.is_dirty = True
    s.receivers[0] = mock.Mock(return_value=None)
    s.clear()
    assert s.is_dirty is False
    assert s.receivers == [weakref.ref(func2)]


def test_signal_flag():
    s = Signal()
    assert s.is_dirty is False
    s.flag()
    assert s.is_dirty is True


@pytest.mark.asyncio
async def test_receiver():
    s = Signal()
    data = []

    @signals.receiver(signal=s)
    async def func(signal, sender, **kwargs):
        data.append((signal, sender, kwargs))

    classes = [loader.get_class(c) for c in (settings.BASE_STARTUP_PIPELINE + settings.STARTUP_PIPELINE)]
    assert len(s.receivers) == 1
    assert s.receivers == [weakref.ref(func)]

    await StartupPipeline(controller=object()).initialise()
    for i, (_signal, _sender, _kwargs) in enumerate(data):
        assert isinstance(_signal, signals.Signal)
        assert isinstance(_sender, (classes[i],))
        assert _kwargs == {}

    with pytest.raises(TypeError) as e:

        @signals.receiver(signal=s)
        def func(signal, sender, **kwargs):
            pass

    assert s.receivers == [weakref.ref(func)]
    assert "'func' is not coroutine function" in str(e)

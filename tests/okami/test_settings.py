import os

import pytest

from okami import settings
from okami.cfg import Settings
from tests.factory import Factory


def test_settings___init__():
    assert Settings()._settings is None


def test_settings__setup():
    assert settings.DEBUG is False
    setattr(settings, "ABCD", 123)
    assert settings.ABCD == 123
    os.environ.pop("OKAMI_SETTINGS")
    Settings()._setup()
    assert settings.ABCD == 123


def test_settings___getattr__(factory: Factory):
    with pytest.raises(AttributeError):
        str(settings.ABC)
    with factory.settings as s:
        s.set(dict(ABC=123))
        assert settings.ABC == 123

    settings._settings = None
    assert settings.DEBUG is False


def test_settings___delattr__():
    assert settings.DEBUG is False
    del settings.DEBUG
    assert not hasattr(settings, "DEBUG")
    with pytest.raises(AttributeError):
        str(settings.DEBUG)

    assert not hasattr(settings, "DEBUG")
    with pytest.raises(TypeError) as e:
        del settings._settings
    assert "Can't delete '_settings'." in str(e)

    assert not hasattr(settings, "DEBUG")
    settings._setup()
    assert hasattr(settings, "DEBUG")
    assert settings.DEBUG is False
    settings._settings = None
    del settings.DEBUG
    with pytest.raises(AttributeError):
        str(settings.DEBUG)


def test_settings_configure():
    with pytest.raises(RuntimeError) as e:
        settings.configure()
    assert "Settings already configured." in str(e)

    settings._settings = None
    settings.configure()

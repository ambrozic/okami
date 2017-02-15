import importlib
import os


class Settings:
    def __init__(self):
        self._settings = None

    def _setup(self):
        from okami.configuration import default

        self._settings = type("_settings", (object,), {})

        for setting in dir(default):
            if setting.isupper():
                setattr(self._settings, setting, getattr(default, setting))

        okami_settings = os.environ.get("OKAMI_SETTINGS")
        if not okami_settings:
            raise RuntimeError("Missing settings module 'OKAMI_SETTINGS'")

        module = importlib.import_module(okami_settings)
        for setting in dir(module):
            if setting.isupper():
                value = getattr(module, setting)
                setattr(self._settings, setting, value)

    def __getattr__(self, name):
        if self._settings is None:
            self._setup()
        return getattr(self._settings, name)

    def __delattr__(self, name):
        if name == "_settings":
            raise TypeError("Can't delete '_settings'.")
        if self._settings is None:
            self._setup()
        delattr(self._settings, name)

    def configure(self):
        if self._settings is not None:
            raise RuntimeError("Settings already configured.")
        self._setup()


settings = Settings()

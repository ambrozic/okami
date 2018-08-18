from okami import api, settings, Item


class Settings:
    def __enter__(self):
        self.default = dict()
        for k, v in settings._settings.__dict__.items():
            if k.isupper():
                self.default[k] = v
        return self

    def set(self, dictionary: dict):
        for k, v in dictionary.items():
            setattr(settings._settings, k, v)

    def __exit__(self, exc, value, traceback):
        for k, v in self.default.items():
            setattr(settings._settings, k, v)


class Product(Item):
    def __init__(self, iid="IID", name="NAME", images=None):
        self.iid = iid
        self.name = name
        self.images = images or []

    def to_dict(self):
        return dict(
            iid=self.iid,
            name=self.name,
        )


class Spider(api.Spider):
    name = "test-spider"
    urls = dict(
        start=["//a[contains(@href, 'start')]/@href"],
        allow=["//a[contains(@href, 'allow')]/@href"],
        avoid=["//a[contains(@href, 'avoid')]/@href"],
    )


class ProductFactory:
    def create(self, **kwargs):
        return Product(**kwargs)


class SpiderFactory:
    def create(self, **kwargs):
        return Spider()


class Objects:
    product = ProductFactory()
    spider = SpiderFactory()


class Factory:
    settings = Settings()
    obj = Objects()

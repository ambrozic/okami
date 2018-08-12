# Spiders

Spiders are the business end of okami. Their main function is to provide URL parsing rules and web page content parsing for a particular web page.

Spiders are fed [Task](api.md#task) and [Response](api.md#response) object after [HttpMiddleware](middlewares.md#http-middleware) and [Downloader](downloader.md) are finished processing [Request](api.md#request) object for a page. [Response](api.md#response) object contains complete HTTP response.

Spiders, if needed, can also handle authentication and session for HTTP negotiation with website.

Full scraping cycle is defined in [process](architecture.md#process) section on architecture page.


## Notes

- Spiders should have unique class property `name`.
- Keep your spiders in a python package. You can have multiple packages. Define them in [settings](settings.md) module.
    - `SPIDERS=["path.to.package.spiders"]`
- Okami finds and loads spiders from this packages using property `name`.


## Development

Make sure everything is properly configured. During development you can test run your spider using command below:

- `okami process spider-name url`

This will run a spider with name `spider-name` against a page at `url`. Output should be a *JSON* representation of a list of [Item](api.md#item) objects.

## Details

Below are required and optional implementation details for every spider.

#### Required

- `Spider.name` - required and it should be unique
- `Spider.urls` dictionary defines rules used by okami to parse a list of valid URLs from page content for further website processing.
    - `Spider.urls.start` - URLs used as starting URLs for processing website
    - `Spider.urls.allow` - Allowed URLs for further website processing
    - `Spider.urls.avoid` - URLs that are avoided during website processing

- `Spider.items <okami.Spider.items>` method receives [Task](api.md#task) object, processes page content and returns a list of [Item](api.md#item) objects.

#### Optional

- `Spider.tasks <okami.Spider.tasks>` method is optionally used in case `Spider.urls` does not get all URLs. Method receives [Task](api.md#task) object, processes page content and returns a list of [Task](api.md#task) objects with **urls** and optionally **data** for further processing.
- `Spider.session <okami.Spider.session>` method is optionally used to handle authentication etc.
- `Spider.request <okami.Spider.request>` method is optionally used to define a dictionary of extra arguments passed into [Request](api.md#request) object used by [Downloader](downloader.md) to create an HTTP request and download a page
- `Spider.delta <okami.Spider.hash>` method is optionally used to provide a custom delta key in case delta scraping mode is enabled


## Example

Below is an example [Spider](api.md#spider) implementation.
```
class Example(Spider):
    """
    An example Spider implementation.
    """

    name = "example.com"
    urls = dict(
        start=["http://localhost:8000/"],
        allow=[
            "//nav//a/@href",
            "//div[@id='product-list']//div//a/@href",
        ],
        avoid=[
            "//a[contains(@href, '/about/')]/@href",
            "//a[contains(@href, '/sale/')]/@href",
        ]
    )

    async def items(self, task, response):
        items = []
        document = lxml.html.document_fromstring(html=response.text)
        products = document.xpath("//div[@class='product']")
        for product in products:
            iid = int(product.xpath(".//@product-id")[0])
            name = product.xpath(".//h2/text()")[0]
            desc = product.xpath(".//p/text()")[0]
            category = product.xpath(".//span/text()")[0]
            price = float(product.xpath(".//em/text()")[0])
            images = product.xpath(".//div//img/@src")
            item = Product(
                iid=iid,
                url=str(response.url),
                name=name,
                category=category,
                desc=desc,
                price=price,
                images=images,
            )
            items.append(item)
        return items
```

And an example [Item](api.md#item) implementation.
```
class Product(Item):
    """
    An example Item object implementation. You will of course have your own.
    """

    def __init__(self, iid, url, name, category, desc, price, images=None):
        self.iid = iid
        self.url = url
        self.name = name
        self.category = category
        self.desc = desc
        self.price = price
        self.images = images or []

    def to_dict(self):
        return dict(
            iid=self.iid,
            url=self.url,
            name=self.name,
            category=self.category,
            desc=self.desc,
            price=self.price,
            images=self.images,
        )
```

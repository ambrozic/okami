import asyncio
import base64
import logging
import random

import lxml.html
from aiohttp import web

from okami import settings, Item, Spider

log = logging.getLogger(__name__)


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

    async def hash(self, task, response):
        return task.url


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


class HTTPService:
    CATEGORIES = dict(
        backpacks=(42, 6),
        bags=(41, 5),
        belts=(51, 12),
        boots=(32, 11),
        briefcases=(43, 3),
        coats=(22, 15),
        gloves=(53, 7),
        hats=(52, 10),
        jackets=(23, 12),
        jeans=(11, 23),
        jewelery=(56, 21),
        luggage=(44, 4),
        pants=(13, 21),
        sandals=(33, 9),
        scarves=(55, 7),
        shirts=(14, 32),
        shoes=(31, 14),
        shorts=(12, 22),
        sneakers=(34, 8),
        suits=(21, 11),
        ties=(54, 11),
        underwear=(15, 9),
    )
    TEMPLATE = """<!DOCTYPE html>
    <html lang="en">
    <head>
    \t<title>{title}</title>
    </head>
    <body>
    \t<nav>\n\t\t<ul>\n{navigation}\t\t</ul>\n\t</nav>{product}\n
    \t<div id=\"product-list\">{products}\t</div>\n</body>\n</html>"""
    TEMPLATE_NAVIGATION = "\t\t\t<li><a href=\"/{0}/\">{0}</a></li>\n"
    TEMPLATE_IMAGE = "\t\t\t<img src=\"{}\"/>\n"
    TEMPLATE_PRODUCT = """
    \t\t<div class="{clazz}" product-id="{pid}" product-slug="{slug}">
    \t\t\t<h2>{name}</h2>
    \t\t\t<p>{desc}</p>
    \t\t\t<span>{cat}</span>
    \t\t\t<em>{price}</em>
    \t\t\t<div class="images">\n{images}\t\t</div>
    \t\t\t<a href="/{cat}/{pid}/">{name}</a>
    \t\t</div>
    """
    IMAGE = """iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAACC0lEQVRYR+1WQXISURB9b9ixCZ5AbuBkL/Cz1IlVnxOoN0hOEDyBegLj
    CRjLTFxmAPeQE0huQDbZMc/qIQjCJBDKSsqq6d3839Pv9ev+/zfxxMYnxsf/QaDRPm9RcgQ8gBpR3U/jg8myes5f1ISbIYCJgFhkOui+7m1SuFCBBaA
    cSLcaRMKHfhx1ltebPumQOFkDlFKBaQB8S+NotLqfE3A+CTOgRcABOWht4ahLiXmQCjgSMwuyJ6FjWZpfrg5hhK6pIJxCIWFrcgBf/IklTQCLBSPUM0
    Js+WQIIlxidqVb1hVU43Wpk1CEAe+tZHNNwa1m6fyP+hSZmxHK1Xy+IIQRW+1kbIuZ8L6CIE3jV/Z9r1m9p7jxBOrmKGA8iKPTTf/N1J4RCogvAK7Y9
    GenJN9S2C+q0TZBH+pjJRcxlPSVDZ+8MzaZdDyIDz89NNgu/g1/dhSQH011miRi9ktAr9+N1jp+F4BN/zTbSUprelWf5adg3ge9bvQoF1OrnQjQZa97
    GOaA8z6AMALsqMyNEyI43qYxi7LO1cXUmm3JWLNTJ+FzP46OcgINf+4DqlsUpOjS2STxfP/OywnAVNnBz/iNlaLYXvrvrsLg4l8QmIMVIZUESgVKBUo
    FSgVKBTYqAGEMaOOcWPyksQ6ivtNjdDsp2fS7mGK3fYf/9ruiAnfXTPEoE9B9vEsCvwFTE6VLUurtxwAAAABJRU5ErkJggg=="""

    def __init__(self, address, multiplier, delay=0.0):
        self.address = address
        self.multiplier = multiplier
        self.delay = delay
        try:
            self.app = web.Application(debug=settings.DEBUG)
            self.app.router.add_routes(
                [
                    web.get(path="/", handler=self.view_index, name="index"),
                    web.get(path="/images/{cat}/{iid}.png", handler=self.view_image, name="image"),
                    web.get(path="/{cat}/", handler=self.view_category, name="category"),
                    web.get(path="/{cat}/{pid}/", handler=self.view_product, name="product"),
                ]
            )
            self.navigation = None

        except Exception as e:
            log.exception(e)

    def start(self):
        host, port = self.address.split(":")
        items = sum(map(lambda a: a[1] * self.multiplier, self.CATEGORIES.values())) * 2
        print("Okami Example Server at http://{}:{}/ - items: {}, delay: {}".format(host, port, items, self.delay))
        web.run_app(app=self.app, host=host, port=port, print=None)

    def get_product(self, pid, cat):
        if not pid or not cat:
            return dict()
        num = int(self.multiplier * self.CATEGORIES[cat.split("-")[1]][1])
        return dict(
            pid=pid,
            cat=cat,
            name="name {}".format(pid),
            slug="{}-name-{}".format(cat, pid),
            desc="some desc {}".format(pid),
            price=random.randint(num * 100, num * 100 * 3) / 100.0,
            images=["http://{}/images/name-{}/{}.png".format(self.address, i, i) for i in range(4, 6 + int(pid) % 9)],
        )

    def get_products(self, cat=None):
        products = []
        if not cat:
            return products

        num = self.multiplier * self.CATEGORIES[cat.split("-")[1]][1]
        cid = self.CATEGORIES[cat.split("-")[1]][0]
        g = cat.split("-")[0]

        for i in range(num):
            pid = int("{}{}00{}".format("1" if g == "men" else "2", cid, i))
            products.append(self.get_product(pid=pid, cat=cat))
        return products

    def render_navigation(self):
        navigation = sorted(["{}-{}".format(g, k) for k, _ in self.CATEGORIES.items() for g in ["men", "women"]])
        return "".join(self.TEMPLATE_NAVIGATION.format(item) for item in navigation)

    def render_product(self, product, clazz):
        images = "".join(self.TEMPLATE_IMAGE.format(image) for image in (product or {}).get("images", []))
        return self.TEMPLATE_PRODUCT.format(**{**product, **dict(clazz=clazz, images=images)}) if product else ""

    def render_template(self, data):
        template = dict(
            title=data.get("title"),
            navigation=self.render_navigation(),
            product=self.render_product(data.get("product"), "product"),
            products="".join(self.render_product(product, "product-item") for product in data.get("products", [])),
        )
        return str.encode(self.TEMPLATE.format(**template))

    async def view_index(self, request):
        return web.Response(
            body=self.render_template(
                data=dict(title="Example")
            ),
            content_type="text/html",
        )

    async def view_category(self, request):
        cat = request.match_info.get("cat")
        return web.Response(
            body=self.render_template(
                data=dict(title="Example | {}".format(cat), products=self.get_products(cat=cat))
            ),
            content_type="text/html",
        )

    async def view_product(self, request):
        pid = request.match_info.get("pid")
        cat = request.match_info.get("cat")
        await asyncio.sleep(self.delay)
        return web.Response(
            body=self.render_template(
                data=dict(title="Example | {} | {}".format(cat, pid), product=self.get_product(pid, cat))
            ),
            content_type="text/html",
        )

    async def view_image(self, request):
        resp = web.StreamResponse()
        resp.content_type = "image/png"
        await resp.prepare(request)
        await resp.write(base64.b64decode(self.IMAGE))
        return resp

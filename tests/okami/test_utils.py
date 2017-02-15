from okami import utils
from tests.factory import Factory


def test_filter_urls(factory: Factory):
    for domains, urls, result in [
        (
            ["https://domain.com", "https://domain.com/"],
            ["https://domain.com/abc/dfe/?a=1&b=2#abcd", "https://domain.com/abc/dfe/?a=11&b=22#abcd"],
            {"https://domain.com/abc/dfe/?a=1&b=2#abcd", "https://domain.com/abc/dfe/?a=11&b=22#abcd"}
        ),
        (
            ["https://domain.com:8000", "https://domain.com:8000/"],
            ["https://domain.com:8000/abc/dfe/?a=1&b=2#abcd", "https://domain.com:8000/abc/dfe/?a=11&b=22#abcd"],
            {"https://domain.com:8000/abc/dfe/?a=1&b=2#abcd", "https://domain.com:8000/abc/dfe/?a=11&b=22#abcd"}
        ),
        (
            ["https://domain.com:8000", "https://domain.com:8000/"],
            ["https://domain.com:8000/abc/dfe/?a=1&b=2#abcd", "https://www.domain.com:8000/abc/dfe/?a=11&b=22#abcd"],
            {"https://domain.com:8000/abc/dfe/?a=1&b=2#abcd"}
        ),
        (
            ["https://domain.com:8000", "https://domain.com:8000/"],
            ["https://domain.com/abc/dfe/?a=1&b=2#abcd", "https://domain.com/abc/dfe/?a=11&b=22#abcd"],
            set()
        ),
    ]:
        assert result == utils.filter_urls(domains, urls)


def test_parse_domain_url(factory: Factory):
    for domain, url, result in [
        ("https://127.0.0.1", "https://127.0.0.1/abc/dfe/?a=1&b=2", "https://127.0.0.1/abc/dfe/?a=1&b=2"),
        ("http://127.0.0.1", "http://127.0.0.1/abc/dfe/?a=1&b=2#abcd", "http://127.0.0.1/abc/dfe/?a=1&b=2#abcd"),
        ("", "https://127.0.0.1/abc/dfe/?a=1&b=2#abcd", "https://127.0.0.1/abc/dfe/?a=1&b=2#abcd"),
        ("https://127.0.0.1", "/abc/dfe/?a=1&b=2", "https://127.0.0.1/abc/dfe/?a=1&b=2"),
        ("http://127.0.0.1:800", "http://127.0.0.1:800/abc/dfe?a=1&b=2", "http://127.0.0.1:800/abc/dfe?a=1&b=2"),
        ("https://127.0.0.1:8000", "/abc/dfe?a=1&b=2", "https://127.0.0.1:8000/abc/dfe?a=1&b=2"),

        ("http://www.domain.com", "http://www.domain.com/abc/dfe/?a=1&b=2", "http://www.domain.com/abc/dfe/?a=1&b=2"),
        ("http://www.abc.com", "http://www.domain.com/abc/dfe/?a=1&b=2", "http://www.domain.com/abc/dfe/?a=1&b=2"),
        ("", "https://www.domain.com/abc/dfe/?a=1&b=2", "https://www.domain.com/abc/dfe/?a=1&b=2"),
        ("https://www.domain.com", "/abc/dfe/?a=1&b=2", "https://www.domain.com/abc/dfe/?a=1&b=2"),
        ("https://www.domain.com:8000", "/abc/dfe?a=1&b=2", "https://www.domain.com:8000/abc/dfe?a=1&b=2"),

        ("https://domain.com", "https://domain.com/abc/dfe/?a=1&b=2", "https://domain.com/abc/dfe/?a=1&b=2"),
        ("", "https://domain.com/abc/dfe/?a=1&b=2", "https://domain.com/abc/dfe/?a=1&b=2"),
        ("https://domain.com", "/abc/dfe/?a=1&b=2", "https://domain.com/abc/dfe/?a=1&b=2"),
        ("https://domain.com:8000", "/abc/dfe?a=1&b=2", "https://domain.com:8000/abc/dfe?a=1&b=2"),
        ("https://www.domain.com:8000", "/abc/dfe?a=1&b=2", "https://www.domain.com:8000/abc/dfe?a=1&b=2"),
    ]:
        assert result == utils.parse_domain_url(domain, url)


def test_slow_filter_urls(factory: Factory):
    pass


def test_slow_parse_domain_url(factory: Factory):
    pass

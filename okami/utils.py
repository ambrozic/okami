import json
import re
import urllib.parse

RE_DOMAIN = re.compile(
    pattern="^((http[s]?|ftp):\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n]+)(:[0-9]{2,6})?", flags=re.UNICODE | re.IGNORECASE
)


def slow_parse_domain_url(domain, url):
    scheme, netloc, *_ = urllib.parse.urlsplit(domain)
    _, netloc2, params, query, fragments = urllib.parse.urlsplit(url)
    if netloc and not netloc2:
        return urllib.parse.urlunsplit((scheme, netloc, params, query, fragments))
    return url


def slow_filter_urls(domains, urls):
    domains = {urllib.parse.urlsplit(d).netloc for d in domains}
    return {u for u in urls if urllib.parse.urlsplit(u).netloc in domains}


def parse_domain_url(domain, url):
    scheme_netloc = RE_DOMAIN.match(url)
    if not scheme_netloc:
        scheme_netloc = RE_DOMAIN.match(domain).group(0)
        return "{}{}".format(scheme_netloc, url)
    return url


def filter_urls(domains, urls):
    dd = {RE_DOMAIN.match(d).group(0) for d in domains}
    return {u for u in urls if RE_DOMAIN.match(u).group(0) in dd}


def pprint(obj):
    dump = json.dumps(obj, sort_keys=True, indent=4, separators=(",", ": "), ensure_ascii=False)
    try:
        import pygments.lexers
        import pygments.styles
        from pygments.formatters.terminal256 import Terminal256Formatter

        lexer = pygments.lexers.get_lexer_by_name("json")
        formatter = Terminal256Formatter(style=pygments.styles.get_style_by_name("native"))
        print(pygments.highlight(dump.encode(), lexer, formatter).strip())
    except ImportError:
        print(dump)

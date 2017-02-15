import json

from okami.engine import Okami


def setup(parser):
    parser.usage = "\n  okami process domain.com http://domain.com/product/123/"
    parser.add_argument("name", type=str, help="spider name")
    parser.add_argument("url", type=str, help="url")
    return parser


def main(options):
    items = Okami.process(name=options.name, url=options.url)
    dump = json.dumps(items, sort_keys=True, indent=4, separators=(",", ": "), ensure_ascii=False).encode()
    try:
        import pygments.lexers
        from pygments.formatters.terminal256 import Terminal256Formatter

        lexer = pygments.lexers.get_lexer_by_name("json")
        formatter = Terminal256Formatter(style=pygments.styles.get_style_by_name("tango"))
        print(pygments.highlight(dump, lexer, formatter))
    except ImportError:
        print(dump)

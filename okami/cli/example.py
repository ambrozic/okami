import logging

from okami.engine import Okami
from okami.example import HTTPService

log = logging.getLogger(__name__)


def setup(parser):
    parser.usage = "\n  okami example server|spider"
    parser.add_argument("process", type=str, help="Run example server or spider")
    parser.add_argument("--address", default="localhost:8000", type=str, help="Config file location")
    parser.add_argument("--name", default="example.com", type=str, help="Spider name")
    parser.add_argument("--multiplier", default=4, type=int, help="category items multiplier")
    return parser


def main(options):
    try:
        if options.process == "server":
            HTTPService(address=options.address, multiplier=options.multiplier).start()
        elif options.process == "spider":
            Okami.start(name=options.name)
        else:
            options.main(options)
    except Exception as e:
        log.exception(e)

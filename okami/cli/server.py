from okami.configuration import settings
from okami.engine import Okami


def setup(parser):
    parser.usage = "\n  okami server {}".format(settings.HTTP_SERVER_ADDRESS)
    parser.add_argument("address", nargs="?", default=settings.HTTP_SERVER_ADDRESS, help="server address (host:port)")
    return parser


def main(options):
    Okami.serve(address=options.address)

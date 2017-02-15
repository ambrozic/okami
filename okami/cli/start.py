from okami.engine import Okami


def setup(parser):
    parser.usage = "\n  okami start domain.com"
    parser.add_argument("name", type=str, help="spider name")
    return parser


def main(options):
    Okami.start(name=options.name)

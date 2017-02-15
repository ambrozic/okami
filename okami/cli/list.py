from okami import loader
from okami.configuration import settings


def setup(parser):
    parser.usage = "\n  okami list"
    return parser


def main(options):
    discovered = dict()

    if settings.SPIDERS:
        for package in settings.SPIDERS:
            discovered.update(loader.get_spiders_classes(entry_point_name=package))

    if discovered:
        print("")
        print("Spiders ({})".format(len(discovered)))
        types = sorted(discovered.items(), key=lambda nc: nc[0])
        width = max(len(n[0]) for n in types)
        for name, clazz in types:
            print(("  {:<%s}  {}:{}" % width).format(name, clazz.__module__, name))
        print("")
    else:
        print("")
        print("No spiders available")
        print("")

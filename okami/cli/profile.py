import asyncio
import cProfile
import os
import pstats

from okami.configuration import settings
from okami.engine import Okami


def setup(parser):
    parser.usage = "\n  okami profile domain.com --sort=cumtime --limit=0.05"
    parser.add_argument("name", type=str, help="spider name")
    parser.add_argument("-s", "--sort", type=str, default="cumtime", help="cProfile sort column")
    parser.add_argument("-o", "--outfile", type=str, default=None, help="Output file - use it for visualisations")
    parser.add_argument("-l", "--limit", type=float, default=0.2, help="Limit output in %, 0.0-1.0")
    parser.add_argument("-f", "--filter", type=str, default=None, help="Filter by filename")
    parser.add_argument("-x", "--strip", action="store_true", help="Strip directories from filename")
    return parser


def main(options):
    profiler = cProfile.Profile()
    profiler.enable()
    Okami.start(name=options.name)
    profiler.disable()

    stats = pstats.Stats(profiler)
    if options.outfile:
        return stats.dump_stats(options.outfile)
    if options.strip:
        stats = stats.strip_dirs()
    stats.sort_stats(options.sort)

    print("")
    print("  Settings:")
    print("    OKAMI_SETTINGS:", settings.OKAMI_SETTINGS or os.environ.get("OKAMI_SETTINGS"))
    print("    LOOP:", asyncio.get_event_loop())
    print("    DEBUG:", settings.DEBUG)
    print("    SPIDERS:", settings.SPIDERS)
    print("    STORAGE:", settings.STORAGE)
    print("    STORAGE_SETTINGS:", settings.STORAGE_SETTINGS)
    print("    CONN_MAX_CONCURRENT_REQUESTS:", settings.CONN_MAX_CONCURRENT_REQUESTS)
    print("    REQUEST_MAX_FAILED:", settings.REQUEST_MAX_FAILED)
    print("    REQUEST_MAX_PENDING:", settings.REQUEST_MAX_PENDING)
    print("    THROTTLE:", settings.THROTTLE)
    print("    THROTTLE_SETTINGS:", settings.THROTTLE_SETTINGS)
    print("")
    print("  Results:")
    stats.print_stats(options.limit, options.filter)

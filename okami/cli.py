import asyncio
import cProfile
import logging
import os
import pstats

import click
import pkg_resources

from okami import loader, settings, utils
from okami.engine import Okami
from okami.example import HTTPService

CTX = dict(
    help_option_names=["-h", "--help"],
)

BASH_COMPLETION = """
_okami_completion() {
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" COMP_CWORD=$COMP_CWORD _OKAMI_COMPLETE=complete $1 ) )
    return 0
}
complete -F _okami_completion -o default okami;
"""

log = logging.getLogger(__name__)


@click.group(context_settings=CTX, invoke_without_command=True, help="Okami command line interface")
@click.option("--version", "-V", is_flag=True, help="Print version")
@click.option("--setup", "-s", is_flag=True, help="Install okami bash completion")
@click.pass_context
def main(ctx, version, setup):
    if ctx.invoked_subcommand is None:
        if version:
            click.echo(pkg_resources.get_distribution(__name__.split(".")[0]).version)
        if setup:
            if click.confirm("Install okami bash completion?"):
                path = "/usr/local/etc/bash_completion.d/"
                if not os.path.exists(path):
                    path = "/etc/bash_completion.d/"
                with open(os.path.join(path, "okami_completion"), "w") as f:
                    f.write(BASH_COMPLETION)
                    click.echo("Bash completion installed. Reload bash.")


@main.command(context_settings=CTX, help="Run example server or spider")
@click.argument("process", type=click.Choice(["server", "spider"]))
@click.option("--address", default="127.0.0.1:8000", type=str, help="Server address:port")
@click.option("--name", default="example.com", type=str, help="Spider name")
@click.option("--multiplier", default=4, type=int, help="Category items multiplier")
@click.option("--delay", default=0.0, type=float, help="Product view delay")
def example(process, address, name, multiplier, delay):
    if process == "server":
        HTTPService(address=address, multiplier=multiplier, delay=delay).start()
    if process == "spider":
        Okami.start(name=name)


@main.command(context_settings=CTX, help="List available spiders")
def list():
    discovered = dict()

    if settings.SPIDERS:
        for package in settings.SPIDERS:
            discovered.update(loader.get_spiders_classes(entry_point_name=package))

    if discovered:
        click.echo("")
        click.echo("Spiders ({})".format(len(discovered)))
        types = sorted(discovered.items(), key=lambda nc: nc[0])
        width = max(len(n[0]) for n in types)
        for name, clazz in types:
            click.echo(("  {:<%s}  {}:{}" % width).format(name, clazz.__module__, name))
        click.echo("")
    else:
        click.echo("")
        click.echo("No spiders available")
        click.echo("")


@main.command(context_settings=CTX, help="okami process domain.com http://domain.com/product/123/")
@click.argument("name", nargs=1)
@click.argument("url", nargs=1)
def process(name, url):
    items = Okami.process(name=name, url=url)
    utils.pprint(obj=items)


@main.command(context_settings=CTX, help="okami profile domain.com --sort=cumtime --limit=0.05")
@click.argument("name", type=str)
@click.option("--sort", "-s", type=str, default="cumtime", help="cProfile sort column")
@click.option("--outfile", "-o", type=str, default=None, help="Output file - use it for visualisations")
@click.option("--limit", "-l", type=float, default=0.2, help="Limit output in percentage i.e. 0.0-1.0")
@click.option("--filter", "-f", type=str, default=None, help="Filter by filename")
@click.option("--strip", "-x", is_flag=True, help="Strip directories from filename")
def profile(name, sort, outfile, limit, filter, strip):
    profiler = cProfile.Profile()
    profiler.enable()
    Okami.start(name=name)
    profiler.disable()

    stats = pstats.Stats(profiler)
    if outfile:
        return stats.dump_stats(outfile)
    if strip:
        stats = stats.strip_dirs()
    stats.sort_stats(sort)

    click.echo("")
    click.echo("  Settings:")
    click.echo("    OKAMI_SETTINGS: {}".format(os.environ.get("OKAMI_SETTINGS")))
    click.echo("    LOOP: {}".format(asyncio.get_event_loop()))
    click.echo("    DEBUG: {}".format(settings.DEBUG))
    click.echo("    SPIDERS: {}".format(settings.SPIDERS))
    click.echo("    STORAGE: {}".format(settings.STORAGE))
    click.echo("    STORAGE_SETTINGS: {}".format(settings.STORAGE_SETTINGS))
    click.echo("    CONN_MAX_CONCURRENT_REQUESTS: {}".format(settings.CONN_MAX_CONCURRENT_REQUESTS))
    click.echo("    REQUEST_MAX_FAILED: {}".format(settings.REQUEST_MAX_FAILED))
    click.echo("    REQUEST_MAX_PENDING: {}".format(settings.REQUEST_MAX_PENDING))
    click.echo("    THROTTLE: {}".format(settings.THROTTLE))
    click.echo("    THROTTLE_SETTINGS: {}".format(settings.THROTTLE_SETTINGS))
    click.echo("    DELTA_ENABLED: {}".format(settings.DELTA_ENABLED))
    click.echo("")
    click.echo("  Results:")
    stats.print_stats(limit, filter)


@main.command(context_settings=CTX, help="okami server")
@click.option("--address", default=settings.HTTP_SERVER_ADDRESS, type=str, help="Server address:port")
def server(address):
    Okami.serve(address=address)


@main.command(context_settings=CTX, help="okami shell")
def shell():
    try:
        from IPython import embed

        header = """\033[0;31m
         ██████╗ ██╗  ██╗ █████╗ ███╗   ███╗██╗
        ██╔═══██╗██║ ██╔╝██╔══██╗████╗ ████║██║
        ██║   ██║█████╔╝ ███████║██╔████╔██║██║
        ██║   ██║██╔═██╗ ██╔══██║██║╚██╔╝██║██║
        ╚██████╔╝██║  ██╗██║  ██║██║ ╚═╝ ██║██║
         ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝
        \033[0;32mshell\033[0m
        """
        click.echo(header)
        embed()
    except ImportError as e:
        raise ImportError("IPython is not installed") from e


@main.command(context_settings=CTX, help="okami start spider-name")
@click.argument("name", nargs=1)
def start(name):
    Okami.start(name=name)

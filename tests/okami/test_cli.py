import os
from unittest import mock

from click.testing import CliRunner

import okami
from okami import cli
from tests.factory import Factory


@mock.patch("okami.cli.HTTPService", return_value=mock.Mock())
@mock.patch("okami.cli.Okami", return_value=mock.Mock())
def test_main(m1, m2):
    runner = CliRunner()

    for o in ["-V", "--version"]:
        result = runner.invoke(cli.main, [o])
        assert result.exit_code == 0, o
        assert okami.__version__ in result.output, o

    for o in ["-s", "--setup"]:
        result = runner.invoke(cli.main, [o])
        assert result.exit_code == 0, o
        assert "Install okami bash completion? [y/N]:" in result.output, o

    for o in ["-n", "--non-existent"]:
        result = runner.invoke(cli.main, [o])
        assert result.exit_code == 2
        assert "Error: no such option: {}".format(o) in result.output, o

    for c in ["non-existent", "non_existent"]:
        result = runner.invoke(cli.main, [c])
        assert result.exit_code == 2, c
        assert "Error: No such command \"{}\".".format(c) in result.output, c

    for c, o in [["example", "server"], ["example", "spider"]]:
        result = runner.invoke(cli.main, [c, o])
        assert result.exit_code == 0, (c, o)

    # okami list
    result = runner.invoke(cli.main, ["list"])
    assert result.exit_code == 0
    assert "Spiders (1)\n  example.com  okami.example:example.com" in result.output

    # okami process
    result = runner.invoke(cli.main, ["process"])
    assert result.exit_code == 2
    assert "Missing argument \"name\"" in result.output
    result = runner.invoke(cli.main, ["process", "url"])
    assert result.exit_code == 2
    assert "Missing argument \"url\"" in result.output
    result = runner.invoke(cli.main, ["process", "name"])
    assert result.exit_code == 2
    assert "Missing argument \"url\"" in result.output

    # okami profile
    result = runner.invoke(cli.main, ["profile"])
    assert result.exit_code == 2
    assert "Missing argument \"name\"" in result.output

    # okami server
    result = runner.invoke(cli.main, ["server"])
    assert result.exit_code == 0
    assert "" == result.output


@mock.patch("okami.cli.HTTPService", return_value=mock.Mock())
@mock.patch("okami.cli.Okami", return_value=mock.Mock())
def test_example(m1, m2):
    runner = CliRunner()
    for o in ["server"]:
        result = runner.invoke(cli.example, [o])
        assert result.exit_code == 0, o
    for o in ["spider"]:
        result = runner.invoke(cli.example, [o])
        assert result.exit_code == 0, o

    for o in ["-n", "--non-existent"]:
        result = runner.invoke(cli.example, [o])
        assert result.exit_code == 2, o
        assert "Error: no such option: {}".format(o) in result.output, o

    for c in ["non-existent", "non_existent"]:
        result = runner.invoke(cli.example, [c])
        assert result.exit_code == 2, c
        assert "for \"process\": invalid choice: {}. (choose from server, spider)".format(c) in result.output, c


def test_list(factory: Factory):
    runner = CliRunner()

    result = runner.invoke(cli.list)
    assert result.exit_code == 0
    assert "Spiders (1)\n  example.com  okami.example:example.com" in result.output

    for o in ["-n", "--non-existent"]:
        result = runner.invoke(cli.list, [o])
        assert result.exit_code == 2, o
        assert "Error: no such option: {}".format(o) in result.output, o

    for c in ["non-existent", "non_existent"]:
        result = runner.invoke(cli.list, [c])
        assert result.exit_code == 2, c
        assert "Got unexpected extra argument ({})".format(c) in result.output, c

    with factory.settings as s:
        s.set(dict(SPIDERS=[]))
        result = runner.invoke(cli.list)
        assert result.exit_code == 0
        assert "\nNo spiders available\n\n" == result.output


@mock.patch("okami.cli.Okami", return_value=mock.Mock())
def test_process(m1):
    runner = CliRunner()
    result = runner.invoke(cli.process)
    assert result.exit_code == 2
    assert "Missing argument \"name\"" in result.output

    result = runner.invoke(cli.process, ["name"])
    assert result.exit_code == 2
    assert "Missing argument \"url\"" in result.output

    result = runner.invoke(cli.process, ["name", "url"])
    assert result.exit_code == -1
    assert result.exc_info[0] == TypeError


@mock.patch("okami.cli.Okami", return_value=mock.Mock())
def test_profile(m1, tmpdir):
    runner = CliRunner()
    result = runner.invoke(cli.profile)
    assert result.exit_code == 2
    assert "Missing argument \"name\"" in result.output

    for o in ["--sort", "-s"]:
        result = runner.invoke(cli.profile, ["name", o, "tottime"])
        assert result.exit_code == 0, o
        assert "OKAMI_SETTINGS: tests.settings" in result.output, o

    for o in ["--outfile", "-o"]:
        fn = os.path.join(tmpdir, "okami.profile")
        result = runner.invoke(cli.profile, ["name", o, fn])
        assert os.path.exists(fn)
        assert result.exit_code == 0, o
        assert "" == result.output, o

    for o in ["--limit", "-l"]:
        result = runner.invoke(cli.profile, ["name", o, 0.1])
        assert result.exit_code == 0, o
        assert "OKAMI_SETTINGS: tests.settings" in result.output, o

    for o in ["--filter", "-f"]:
        result = runner.invoke(cli.profile, ["name", o, "filter"])
        assert result.exit_code == 0, o
        assert "OKAMI_SETTINGS: tests.settings" in result.output, o

    for o in ["--strip", "-x"]:
        result = runner.invoke(cli.profile, ["name", o])
        assert result.exit_code == 0, o
        assert "OKAMI_SETTINGS: tests.settings" in result.output, o

    for o in ["-n", "--non-existent"]:
        result = runner.invoke(cli.profile, [o])
        assert result.exit_code == 2, o
        assert "Error: no such option: {}".format(o) in result.output, o

    for c in ["non-existent", "non_existent"]:
        result = runner.invoke(cli.profile, ["name", c])
        assert result.exit_code == 2, c
        assert "Got unexpected extra argument ({})".format(c) in result.output, c


@mock.patch("okami.cli.Okami", return_value=mock.Mock())
def test_server(m1):
    runner = CliRunner()
    result = runner.invoke(cli.server)
    assert result.exit_code == 0
    assert "" in result.output

    result = runner.invoke(cli.server, ["--address", "address:port"])
    assert result.exit_code == 0
    assert "" in result.output

    result = runner.invoke(cli.server, ["--address"])
    assert result.exit_code == 2
    assert "Error: --address option requires an argument" in result.output

    for o in ["-n", "--non-existent"]:
        result = runner.invoke(cli.server, [o])
        assert result.exit_code == 2, o
        assert "Error: no such option: {}".format(o) in result.output, o

    for c in ["non-existent", "non_existent"]:
        result = runner.invoke(cli.server, [c])
        assert result.exit_code == 2, c
        assert "Got unexpected extra argument ({})".format(c) in result.output, c


def test_shell():
    try:
        import IPython  # noqa
        runner = CliRunner()
        result = runner.invoke(cli.shell)
        assert "    shell\n" in result.output
    except ImportError:
        runner = CliRunner()
        result = runner.invoke(cli.shell)
        assert result.exit_code == -1
        assert "IPython is not installed" in str(result.exception)


@mock.patch("okami.cli.Okami", return_value=mock.Mock())
def test_start(m1):
    runner = CliRunner()
    result = runner.invoke(cli.start, ["name"])
    assert result.exit_code == 0
    assert "" == result.output

    result = runner.invoke(cli.start)
    assert result.exit_code == 2
    assert "Missing argument \"name\"." in result.output

    for o in ["-n", "--non-existent"]:
        result = runner.invoke(cli.start, [o])
        assert result.exit_code == 2, o
        assert "Error: no such option: {}".format(o) in result.output, o

    for c in ["non-existent", "non_existent"]:
        result = runner.invoke(cli.start, ["name", c])
        assert result.exit_code == 2, c
        assert "Got unexpected extra argument ({})".format(c) in result.output, c

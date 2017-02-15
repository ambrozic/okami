def setup(parser):
    parser.usage = "\n  okami shell"
    return parser


def main(options):
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
        print(header)
        embed()
    except ImportError:
        pass
    else:
        return
    # no IPython, raise ImportError
    raise ImportError("No IPython")

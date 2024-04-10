import sys
import subprocess
from signal import signal, SIGINT, SIG_IGN

import click


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("slab")
@click.argument("args", nargs=-1)
def main(slab, args):
    signal(SIGINT, SIG_IGN)
    subprocess.run([sys.executable, "-m", f"slab.{slab}", *args])


if __name__ == "__main__":
    main()

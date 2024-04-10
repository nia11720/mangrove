import os
import sys
import subprocess
from time import sleep
from signal import signal, SIGINT


def walk():
    for root, dirs, files in os.walk("src"):
        dir = os.path.basename(root)
        if dir.startswith(("__", ".")) or dir.endswith(".eff-info"):
            dirs.clear()
            continue

        for file in files:
            file = os.path.join(root, file)
            mtime = os.stat(file).st_mtime
            yield file, mtime


def main():
    watched = dict(walk())
    cmd = [sys.executable, "-m", "slab.start", *sys.argv[1:]]
    p = subprocess.Popen(cmd)
    signal(SIGINT, lambda sig, frame: p.kill() or exit())

    while True:
        sleep(1)
        for file, mtime in walk():
            if file not in watched or watched[file] < mtime:
                print(f"\n------ {file} created or changed ------\n")
                watched[file] = mtime

                p.kill()
                p = subprocess.Popen(cmd)
                break


if __name__ == "__main__":
    main()

import os
import sys
import time
import subprocess


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


wsgi_start = lambda: subprocess.Popen([sys.executable, "-m", "mangrove"])
huey_start = lambda: subprocess.Popen([sys.executable, "-m", "mangrove.huey"])


def main():
    watched = dict(walk())

    p1 = wsgi_start()
    p2 = huey_start()

    while True:
        time.sleep(1)
        for file, mtime in walk():
            if file not in watched or watched[file] < mtime:
                print(f"\n------ {file} created or changed ------\n")
                watched[file] = mtime

                p1.kill()
                p2.kill()
                p1 = wsgi_start()
                p2 = huey_start()
                break


if __name__ == "__main__":
    main()

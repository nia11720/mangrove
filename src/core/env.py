import os

USER_AGENT = "python-httpx/0.28.1"

with open(os.path.expanduser("~/.mangrove/env.py")) as fp:
    exec(fp.read())

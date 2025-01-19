import os

USER_AGENT = "python-httpx/0.28.1"
REDIS_URL = "redis://localhost:6379"

with open(os.path.expanduser("~/.mangrove/env.py")) as fp:
    exec(fp.read())

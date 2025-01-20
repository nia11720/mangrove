from logging import getLogger, INFO

from werkzeug.serving import ForkingWSGIServer

from core.env import PORT
from core.redis import RedisHandler
from mangrove import app


def main():
    logger = getLogger("werkzeug")
    logger.setLevel(INFO)
    logger.addHandler(RedisHandler())

    server = ForkingWSGIServer("localhost", PORT, app)
    server.serve_forever()


if __name__ == "__main__":
    main()

from logging import getLogger, INFO, Formatter

from huey.constants import WORKER_PROCESS

from core import huey
from core.redis import RedisHandler
import mangrove


def main():
    formatter = Formatter("{asctime}: {process} - {message}", style="{")

    redis_handler = RedisHandler()
    redis_handler.setFormatter(formatter)

    logger = getLogger("huey")
    logger.setLevel(INFO)
    logger.addHandler(redis_handler)
    getLogger("huey.consumer").disabled = True

    huey.create_consumer(workers=4, worker_type=WORKER_PROCESS).run()


if __name__ == "__main__":
    main()

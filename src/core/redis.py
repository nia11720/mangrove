from logging import Handler

from redis import Redis as _Redis

from .env import REDIS_URL


class Redis(_Redis):
    pools = {}

    def __new__(cls, *, db=0):
        r = cls.pools.get(db, None)
        if r is None:
            r = cls.pools[db] = _Redis.from_url(REDIS_URL, db=db, decode_responses=True)
        return r


class RedisHandler(Handler):
    redis = Redis(db=12)

    def emit(self, record):
        try:
            msg = self.format(record)
            self.redis.lpush(record.name.replace(".", ":"), msg)
        except:
            self.handleError(record)

from redis import Redis as _Redis

from .env import REDIS_URL


class Redis(_Redis):
    pools = {}

    def __new__(cls, *, db=0):
        r = cls.pools.get(db, None)
        if r is None:
            r = cls.pools[db] = _Redis.from_url(REDIS_URL, db=db, decode_responses=True)
        return r

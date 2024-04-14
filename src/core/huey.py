from __future__ import annotations

from huey import PriorityRedisHuey, crontab

from .config import REDIS_URL

import typing as t

if t.TYPE_CHECKING:
    from huey.api import TaskWrapper


class Huey(PriorityRedisHuey):
    def __init__(self, name: str):
        super().__init__(name, url=REDIS_URL, utc=False, results=False)

    @t.overload
    def periodic_task(
        self,
        crontab_str="",
        retries=0,
        retry_delay=0,
        priority=None,
        context=False,
        name=None,
        expires=None,
        **kwargs,
    ) -> TaskWrapper: ...

    def periodic_task(self, crontab_str="", *args, **kwarg):
        return super().periodic_task(crontab(*crontab_str.split()), *args, **kwarg)


huey = Huey("mangrove")

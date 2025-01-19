from huey import PriorityRedisHuey, crontab

from .env import REDIS_URL


class Huey(PriorityRedisHuey):
    def __init__(self, name: str):
        super().__init__(name, url=REDIS_URL, utc=False, results=False)

    def periodic_task(self, crontab_str="", *args, **kwarg):
        """
        * * * * * crontab syntax
        │ │ │ │ │
        │ │ │ │ │
        │ │ │ │ └── Day of the week (0 - 6) (Sunday = 0)
        │ │ │ └──── Month (1 - 12)
        │ │ └────── Day of the month (1 - 31)
        │ └──────── Hour (0 - 23)
        └────────── Minute (0 - 59)
        """
        return super().periodic_task(crontab(*crontab_str.split()), *args, **kwarg)


huey = Huey("mangrove")

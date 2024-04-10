import json as jsonlib
from time import sleep
from datetime import datetime

from flask import Blueprint, request

from core import huey, Redis

bp = Blueprint("test", __name__)

redis = Redis("test")


@huey.periodic_task("*")
def touch():
    pass


@huey.task(context=True)
def occupy_worker(n, task):
    redis.set(
        f"occupied_worker:{task.id}",
        f"{datetime.now()}: occupy {n} seconeds",
        ex=n,
    )
    sleep(n)


@bp.post("/occupy")
def occupy():
    t = request.args.get("t", 0, int)
    occupy_worker(t)
    return "ok"


@bp.get("/sse")
def sse():
    def response():
        with redis.pubsub() as sub:
            sub.subscribe("ch:sse")
            for msg in sub.listen():
                if msg["type"] == "message":
                    yield f"{msg['data']}\n"

    return response()


@bp.post("/message")
def message():
    redis.publish("ch:sse", jsonlib.dumps(request.json))
    return "ok"


@bp.get("/countdown")
def countdown():
    n = request.args.get("n", 0, int)

    def response():
        nonlocal n

        yield f"total: {n}\n"
        while n:
            sleep(1)
            n -= 1
            yield f"remaining: {n}\n"
        yield "done\n"

    return response()

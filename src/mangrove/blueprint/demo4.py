import time
from datetime import datetime

from flask import Blueprint, request

from core import huey, Redis

bp = Blueprint("demo4", __name__)

r = Redis(db=15)


@huey.periodic_task("13 *")
def touch():
    """log"""


@huey.task(context=True)
def sleep(n, task):
    r.set(
        f"demo4:task-{task.id}",
        f"{datetime.now():&Y-%m-%d %H:%M:%S}: sleep {n} seconeds",
        ex=n,
    )
    time.sleep(n)


@bp.post("/sleep")
def sleep2():
    t = request.args.get("t", type=int) or 5
    sleep(t)
    return "ok"


@bp.get("/count")
def count():
    t = request.args.get("t", type=int) or 5

    def response():
        nonlocal t

        yield f"data: total - {t}\n\n"
        while t:
            time.sleep(1)
            t -= 1
            yield f"data: count - {t}\n\n"
        yield "data: done\n\n"

    return response(), {"Content-Type": "text/event-stream"}

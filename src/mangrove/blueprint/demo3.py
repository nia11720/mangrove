from datetime import datetime

from flask import Blueprint, request, abort

from core import Redis

bp = Blueprint("demo3", __name__)
r = Redis(db=15)


@bp.get("/")
def index():
    cursor = 0
    keys = []
    while True:
        cursor, partial_keys = r.scan(cursor=cursor, match="demo3:*")
        keys += partial_keys
        if cursor == 0:
            break

    with r.pipeline() as pipe:
        for key in keys:
            pipe.type(key)
        types = pipe.execute()

        for type, key in zip(types, keys):
            match type:
                case "string":
                    pipe.get(key)
                case "list":
                    pipe.lrange(key, 0, 20)
                case "hash":
                    pipe.hgetall(key)
        vals = pipe.execute()
    return dict(zip(keys, vals))


@bp.post("/touch")
def touch():
    r.set("demo3:atime", str(datetime.now().astimezone()))
    return "ok"


@bp.post("/publish")
def publish():
    message = request.json.get("message")
    if not message or not isinstance(message, str):
        abort(400)

    with r.pipeline() as pipe:
        pipe.lpush("demo3:messages", message)
        pipe.ltrim("demo3:messages", 0, 19)
        pipe.set("demo3:atime", str(datetime.now().astimezone()))
        pipe.execute()

    r.publish("demo3:ch", message)
    return "ok"


@bp.get("/subscribe")
def subscribe():
    def sse_events():
        pubsub = r.pubsub()
        pubsub.subscribe("demo3:ch")

        for message in r.lrange("demo3:messages", 0, 20):
            yield f"data: {message}\n\n"

        for message in pubsub.listen():
            if message["type"] == "message":
                yield f"data: {message['data']}\n\n"

    return sse_events(), {"Content-Type": "text/event-stream"}


@bp.post("/clear")
def clear():
    r.delete("demo3:messages")
    return "ok"

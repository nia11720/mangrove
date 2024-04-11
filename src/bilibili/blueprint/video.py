import json as jsonlib
from urllib.parse import quote

from flask import Blueprint, request, abort, g

from utils import Getter
from bilibili.extensions import redis, httpx, authed_httpx
from bilibili.utils import attach_wrid, DanmakuParser

bp = Blueprint("video", __name__)


@bp.before_request
def before_request():
    g.id = id = request.args.get("id") or abort(400)

    httpx.Referer = f"https://www.bilibili.com/video/{id}"

    if metadata := redis.get(f"video:{id}", json=True):
        g.metadata = Getter(metadata)
    else:
        index()


@bp.get("/")
def index():
    url = f"/x/web-interface/wbi/view/detail?bvid={g.id}"
    res = httpx.get(url)
    data = res.json()["data"]

    video = Getter(data["View"])
    g.metadata = metadata = video[{"bvid", "cid", "aid", "duration", "title", "desc"}]
    metadata["pages"] = Getter(video["pages"])[{"cid", "part", "duration"}]
    redis.set(f"video:{g.id}", metadata, json=True, ex=3600)

    return data


@bp.get("/stream")
def stream():
    cid = request.args.get("cid") or g.metadata["cid"]

    url = f"/x/player/wbi/playurl?bvid={g.id}&cid={cid}&fnval=4048"
    res = httpx.get(url)
    data = res.json()["data"]

    key = {"base_url", "codecs", "mime_type", "id"}
    stream = {
        "audio": Getter(data["dash"]["audio"])[key],
        "video": Getter(data["dash"]["video"])[key],
    }
    redis.set(f"stream:{g.id}-{cid}", stream, json=True, ex=3600)

    return data


@bp.get("/comment")
def comment():
    offset = request.args.get("offset") or ""
    oid = g.metadata["aid"]
    pagination_str = quote(jsonlib.dumps({"offset": offset}))

    url = "/x/v2/reply/wbi/main"
    params = f"oid={oid}&type=1&pagination_str={pagination_str}"
    res = authed_httpx.get(url, params=(params))
    data = res.json()["data"]

    return data


@bp.get("/reply")
def reply():
    root = request.args.get("root")
    pn = request.args.get("pn", type=int) or 1
    oid = g.metadata["aid"]

    url = "/x/v2/reply/reply"
    params = f"oid={oid}&type=1&root={root}&ps=10&pn={pn}"
    res = authed_httpx.get(url, params=attach_wrid(params))
    data = res.json()["data"]

    return data


@bp.get("/danmaku")
def danmaku():
    seg = request.args.get("seg", type=int) or 1
    cid = request.args.get("cid") or g.metadata["cid"]

    url = "/x/v2/dm/wbi/web/seg.so"
    params = f"type=1&oid={cid}&segment_index={seg}"
    res = httpx.get(url, params=attach_wrid(params))
    data = DanmakuParser(res.content).decode()

    return data

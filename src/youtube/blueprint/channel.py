import re

from flask import Blueprint, request, abort, g

from core import Httpx
from utils import Getter
from youtube.extensions import httpx, redis

bp = Blueprint("channel", __name__)


def handle2id(handle):
    if id := redis.get(f"channel:{handle}"):
        return id

    res = Httpx().get(f"https://www.youtube.com/{handle}")
    m = re.search(r'"https://www.youtube.com/channel/(\S+)"', res.text)
    redis.set(f"channel:{handle}", m[1], ex=60 * 60 * 24 * 7)
    return m[1]


@bp.before_request
def before_request():
    id = request.args.get("id") or abort(400)
    g.id = id = handle2id(id) if id.startswith("@") else id

    httpx.Referer = f"https://www.youtube.com/channel/{id}"

    if channel := redis.get(f"channel:{id}", json=True):
        g.tabs = channel["tabs"]
    else:
        index()


@bp.get("/")
def index():
    items_key = "contents.twoColumnBrowseResultsRenderer.tabs"
    data, tabs, _ = httpx.browse(g.id, items_key, params="EghmZWF0dXJlZPIGBAoCMgA%3D")

    channel = Getter(data).get(
        [
            "metadata.channelMetadataRenderer",
            {
                "id": "externalId",
                "name": "title",
                "headimg": "avatar.thumbnails.0.url",
                "des": "description",
                "keywords": "keywords",
            },
        ]
    )

    if tabs and tabs[-1].get("expandableTabRenderer"):
        tabs.pop()

    channel["tabs"] = Getter(tabs).get(
        [
            "tabRenderer",
            {
                "title": "title",
                "params": "endpoint.browseEndpoint.params",
            },
        ]
    )

    g.tabs = channel["tabs"]
    redis.set(f"channel:{g.id}", channel, json=True, ex=60 * 60 * 24)

    return channel


@bp.get("/video")
def video():
    for i, tab in enumerate(g.tabs):
        if tab["title"] == "Videos":
            break

    items_key = (
        f"contents.twoColumnBrowseResultsRenderer.tabs.{i}."
        "tabRenderer.content.richGridRenderer.contents"
    )
    _, items, continuation = httpx.browse(
        g.id, items_key, params="EgZ2aWRlb3PyBgQKAjoA"
    )

    rv = {"continuation": continuation}
    for item in items:
        video = Getter(item).get(
            [
                "richItemRenderer.content.videoRenderer",
                {
                    "id": "videoId",
                    "title": "title.runs.0.text",
                    "duration_text": "lengthText.simpleText",
                    "thumbnail": "thumbnail.thumbnails.0.url",
                    "view_text": "shortViewCountText.simpleText",
                    "publish_text": "publishedTimeText.simpleText",
                },
            ]
        )
        video["desc"] = " • ".join([video.pop("view_text"), video.pop("publish_text")])
        rv.setdefault("items", []).append(video)

    return rv


@bp.get("/live")
def live():
    for i, tab in enumerate(g.tabs):
        if tab["title"] == "Live":
            break

    items_key = (
        f"contents.twoColumnBrowseResultsRenderer.tabs.{i}."
        "tabRenderer.content.richGridRenderer.contents"
    )
    _, items, continuation = httpx.browse(
        g.id, items_key, params="EgdzdHJlYW1z8gYECgJ6AA%3D%3D"
    )

    rv = {"continuation": continuation}
    for item in items:
        live = Getter(item).get(
            [
                "richItemRenderer.content.videoRenderer",
                {
                    "id": "videoId",
                    "title": "title.runs.0.text",
                    "duration_text": "lengthText.simpleText",
                    "thumbnail": "thumbnail.thumbnails.0.url",
                    "view_text": ["viewCountText.runs", "text"],
                    "publish_text": "publishedTimeText.simpleText",
                },
            ]
        )

        if live["duration_text"]:
            live.pop("view_text")
            live["desc"] = live.pop("publish_text")
        else:
            live.pop("duration_text")
            live.pop("publish_text")
            live["desc"] = "".join(live.pop("view_text"))
        rv.setdefault("items", []).append(live)

    return rv


@bp.get("/playlist")
def playlist():
    for i, tab in enumerate(g.tabs):
        if tab["title"] == "Playlists":
            break

    items_key = (
        f"contents.twoColumnBrowseResultsRenderer.tabs.{i}."
        "tabRenderer.content.sectionListRenderer.contents.0.itemSectionRenderer.contents.0.gridRenderer.items"
    )
    _, items, continuation = httpx.browse(
        g.id, items_key, params="EglwbGF5bGlzdHPyBgQKAkIA"
    )

    rv = {"continuation": continuation}
    for item in items:
        playlist = Getter(item).get(
            [
                "gridPlaylistRenderer",
                {
                    "id": "playlistId",
                    "title": "title.runs.0.text",
                    "thumbnail": "thumbnail.thumbnails.0.url",
                    "desc": ["videoCountText.runs", "text"],
                },
            ]
        )
        playlist["desc"] = "".join(playlist["desc"])
        rv.setdefault("items", []).append(playlist)

    return rv

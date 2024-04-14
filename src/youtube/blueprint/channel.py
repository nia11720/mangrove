import re
from datetime import datetime

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

    g.tabs = channel["tabs"] = Getter(tabs)["tabRenderer.title"]
    redis.set(f"channel:{g.id}", channel, json=True, ex=60 * 60 * 24)

    return channel


@bp.get("/video")
def video():
    items_key = (
        f"contents.twoColumnBrowseResultsRenderer.tabs.{g.tabs.index('Videos')}."
        "tabRenderer.content.richGridRenderer.contents"
    )
    _, items, continuation = httpx.browse(
        g.id, items_key, params="EgZ2aWRlb3PyBgQKAjoA"
    )

    rv = {"continuation": continuation}
    for item in items:
        video, view, publish, upcoming = Getter(item).get(
            [
                "richItemRenderer.content.videoRenderer",
                (
                    {
                        "id": "videoId",
                        "title": "title.runs.0.text",
                        "duration_text": "lengthText.simpleText",
                        "thumbnail": "thumbnail.thumbnails.0.url",
                    },
                    "viewCountText.simpleText",
                    "publishedTimeText.simpleText",
                    "upcomingEventData.startTime",
                ),
            ]
        )
        if publish:
            video["desc"] = f"{view} • {publish}"
        else:
            upcoming = datetime.fromtimestamp(int(upcoming))
            video["desc"] = f"Premieres {upcoming}"
        rv.setdefault("items", []).append(video)

    return rv


@bp.get("/live")
def live():
    items_key = (
        f"contents.twoColumnBrowseResultsRenderer.tabs.{g.tabs.index('Live')}."
        "tabRenderer.content.richGridRenderer.contents"
    )
    _, items, continuation = httpx.browse(
        g.id, items_key, params="EgdzdHJlYW1z8gYECgJ6AA%3D%3D"
    )

    rv = {"continuation": continuation}
    for item in items:
        live, duration, view, publish, watching, upcoming = Getter(item).get(
            [
                "richItemRenderer.content.videoRenderer",
                (
                    {
                        "id": "videoId",
                        "title": "title.runs.0.text",
                        "thumbnail": "thumbnail.thumbnails.0.url",
                    },
                    "lengthText.simpleText",
                    "viewCountText.simpleText",
                    "publishedTimeText.simpleText",
                    ["viewCountText.runs", "text"],
                    "upcomingEventData.startTime",
                ),
            ]
        )
        if publish:
            live["duration"] = duration
            live["desc"] = f"{view} • {publish}"
        elif watching:
            live["desc"] = "".join(watching)
        else:
            upcoming = datetime.fromtimestamp(int(upcoming))
            live["desc"] = f"Scheduled for {upcoming}"
        rv.setdefault("items", []).append(live)

    return rv


@bp.get("/playlist")
def playlist():
    items_key = (
        f"contents.twoColumnBrowseResultsRenderer.tabs.{g.tabs.index('Playlists')}."
        "tabRenderer.content.sectionListRenderer.contents.0.itemSectionRenderer.contents.0.gridRenderer.items"
    )
    _, items, continuation = httpx.browse(
        g.id, items_key, params="EglwbGF5bGlzdHPyBgQKAkIA"
    )

    rv = {"continuation": continuation}
    for item in items:
        playlist, desc = Getter(item).get(
            [
                "gridPlaylistRenderer",
                (
                    {
                        "id": "playlistId",
                        "title": "title.runs.0.text",
                        "thumbnail": "thumbnail.thumbnails.0.url",
                    },
                    ["videoCountText.runs", "text"],
                ),
            ]
        )
        playlist["desc"] = "".join(desc)
        rv.setdefault("items", []).append(playlist)

    return rv

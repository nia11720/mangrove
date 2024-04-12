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
    g.id = handle2id(id) if id.startswith("@") else id

    httpx.Referer = f"https://www.youtube.com/channel/{id}"


@bp.get("/")
def index():
    json = {"browseId": g.id, "params": "EghmZWF0dXJlZPIGBAoCMgA%3D"}
    res = httpx.post("/youtubei/v1/browse", json=json)

    channel, tabs = Getter(res.json())[
        [
            "metadata.channelMetadataRenderer",
            {
                "id": "externalId",
                "name": "title",
                "headimg": "avatar.thumbnails.0.url",
                "des": "description",
                "keywords": "keywords",
            },
        ],
        "contents.twoColumnBrowseResultsRenderer.tabs",
    ]

    for tab in tabs:
        if tab.get("tabRenderer"):
            tab = Getter(tab).get(
                [
                    "tabRenderer",
                    {
                        "title": "title",
                        "params": "endpoint.browseEndpoint.params",
                    },
                ]
            )
            channel.setdefault("tabs", []).append(tab)

    return channel


@bp.get("/video")
def video():
    continuation = request.args.get("continuation")

    json = {"browseId": g.id, "params": "EgZ2aWRlb3PyBgQKAjoA"}
    if continuation:
        json["continuation"] = continuation
    res = httpx.post("/youtubei/v1/browse", json=json)

    tabs, continuation_item = Getter(res.json())[
        "contents.twoColumnBrowseResultsRenderer.tabs",
        "onResponseReceivedActions.0.appendContinuationItemsAction.continuationItems",
    ]

    if tabs:
        for tab in tabs:
            if tab["tabRenderer"]["title"] == "Videos":
                break
        items = Getter(tab).get(["tabRenderer.content.richGridRenderer.contents"])
    else:
        items = continuation_item

    rv = {}
    for item in items:
        if item.get("richItemRenderer"):
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
            video["desc"] = " • ".join(
                [video.pop("view_text"), video.pop("publish_text")]
            )
            rv.setdefault("items", []).append(video)
        else:
            rv["continuation"] = Getter(item)[
                "continuationItemRenderer.continuationEndpoint.continuationCommand.token"
            ]

    return rv


@bp.get("/live")
def live():
    continuation = request.args.get("continuation")

    json = {"browseId": g.id, "params": "EgdzdHJlYW1z8gYECgJ6AA%3D%3D"}
    if continuation:
        json["continuation"] = continuation
    res = httpx.post("/youtubei/v1/browse", json=json)

    tabs, continuation_item = Getter(res.json())[
        "contents.twoColumnBrowseResultsRenderer.tabs",
        "onResponseReceivedActions.0.appendContinuationItemsAction.continuationItems",
    ]
    if tabs:
        for tab in tabs:
            if tab["tabRenderer"]["title"] == "Live":
                break
        items = Getter(tab).get(["tabRenderer.content.richGridRenderer.contents"])
    else:
        items = continuation_item

    rv = {}
    for item in items:
        if item.get("richItemRenderer"):
            video = Getter(item).get(
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

            if video["duration_text"]:
                video.pop("view_text")
                video["desc"] = video.pop("publish_text")
            else:
                video.pop("duration_text")
                video.pop("publish_text")
                video["desc"] = "".join(video.pop("view_text"))
            rv.setdefault("items", []).append(video)
        else:
            rv["continuation"] = Getter(item)[
                "continuationItemRenderer.continuationEndpoint.continuationCommand.token"
            ]

    return rv


@bp.get("/playlist")
def playlist():
    continuation = request.args.get("continuation")

    json = {"browseId": g.id, "params": "EglwbGF5bGlzdHPyBgQKAkIA"}
    if continuation:
        json["continuation"] = continuation
    res = httpx.post("/youtubei/v1/browse", json=json)

    tabs, continuation_item = Getter(res.json())[
        "contents.twoColumnBrowseResultsRenderer.tabs",
        "onResponseReceivedActions.0.appendContinuationItemsAction.continuationItems",
    ]
    if tabs:
        for tab in tabs:
            if tab["tabRenderer"]["title"] == "Playlists":
                break
        items = Getter(tab).get(
            [
                "tabRenderer.content.sectionListRenderer.contents.0.itemSectionRenderer.contents.0.gridRenderer.items"
            ]
        )
    else:
        items = continuation_item

    rv = {}
    for item in items:
        if item.get("gridPlaylistRenderer"):
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
        else:
            rv["continuation"] = Getter(item)[
                "continuationItemRenderer.continuationEndpoint.continuationCommand.token"
            ]

    return rv

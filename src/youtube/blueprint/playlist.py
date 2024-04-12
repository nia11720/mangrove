from flask import Blueprint, request, abort

from utils import Getter
from youtube.extensions import httpx

bp = Blueprint("playlist", __name__)


@bp.get("/")
def index():
    id = request.args.get("id") or abort(400)

    httpx.Referer = f"https://www.youtube.com/playlist?list={id}"

    items_key = (
        "contents.twoColumnBrowseResultsRenderer.tabs.0"
        ".tabRenderer.content.sectionListRenderer.contents.0"
        ".itemSectionRenderer.contents.0.playlistVideoListRenderer.contents"
    )
    data, items, continuation = httpx.browse(f"VL{id}", items_key)

    metadata, alert = Getter(data)[
        "header.playlistHeaderRenderer",
        "alerts.0.alertWithButtonRenderer.text.simpleText",
    ]

    if metadata:
        rv = Getter(metadata)[
            {
                "id": "playlistId",
                "title": "title.simpleText",
                "desc": ["stats.0.runs", "text"],
                "owner": {
                    "id": "ownerEndpoint.browseEndpoint.browseId",
                    "name": "ownerText.runs.0.text",
                },
            }
        ]
        rv["desc"] = "".join(rv["desc"])
    else:
        rv = {}

    if alert:
        rv["alert"] = alert

    rv["continuation"] = continuation
    for item in items:
        video = Getter(item).get(
            [
                "playlistVideoRenderer",
                {
                    "id": "videoId",
                    "title": "title.runs.0.text",
                    "duration": "lengthSeconds",
                    "thumbnail": "thumbnail.thumbnails.0.url",
                    "desc": ["videoInfo.runs", "text"],
                },
            ]
        )
        video["desc"] = "".join(video["desc"])
        rv.setdefault("items", []).append(video)

    return rv

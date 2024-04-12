from flask import Blueprint, request, abort

from utils import Getter
from youtube.extensions import httpx

bp = Blueprint("playlist", __name__)


@bp.get("/")
def index():
    id = request.args.get("id") or abort(400)
    continuation = request.args.get("continuation")

    httpx.Referer = f"https://www.youtube.com/playlist?list={id}"

    json = {"browseId": f"VL{id}"}
    if continuation:
        json["continuation"] = continuation
    res = httpx.post("/youtubei/v1/browse", json=json)

    metadata, alert, items, continuation_items = Getter(res.json())[
        "header.playlistHeaderRenderer",
        "alerts.0.alertWithButtonRenderer.text.simpleText",
        (
            "contents.twoColumnBrowseResultsRenderer.tabs.0"
            ".tabRenderer.content.sectionListRenderer.contents.0"
            ".itemSectionRenderer.contents.0.playlistVideoListRenderer.contents"
        ),
        "onResponseReceivedActions.0.appendContinuationItemsAction.continuationItems",
    ]

    if metadata:
        rv = Getter(metadata)[
            {
                "id": "playlistId",
                "title": "title.simpleText",
                "desc": ["stats.0.runs", "text"],
                "owner": {
                    "id": "ownerEndpoint.browseEndpoint.browseId",
                    "handle": "ownerEndpoint.browseEndpoint.canonicalBaseUrl",
                    "name": "ownerText.runs.0.text",
                },
            }
        ]
        rv["desc"] = "".join(rv["desc"])
    else:
        rv = {}

    if alert:
        rv["alert"] = alert

    for item in items or continuation_items:
        if video := item.get("playlistVideoRenderer"):
            video = Getter(video)[
                {
                    "id": "videoId",
                    "title": "title.runs.0.text",
                    "duration": "lengthSeconds",
                    "thumbnail": "thumbnail.thumbnails.0.url",
                    "desc": ["videoInfo.runs", "text"],
                }
            ]
            video["desc"] = "".join(video["desc"])
            rv.setdefault("items", []).append(video)
        else:
            rv["continuation"] = Getter(item)[
                "continuationItemRenderer.continuationEndpoint.continuationCommand.token"
            ]

    return rv

from flask import Blueprint, request, abort

from utils import Getter
from youtube.extensions import httpx

bp = Blueprint("playlist", __name__)


@bp.get("/")
def index():
    id = request.args.get("id") or abort(400)

    httpx.Referer = f"https://www.youtube.com/playlist?list={id}"
    res = httpx.post("/youtubei/v1/browse", json={"browseId": f"VL{id}"})

    playlist = Getter(res.json())[
        {
            "alert": "alerts.0.alertWithButtonRenderer.text.simpleText",
            "metadata": [
                "header.playlistHeaderRenderer",
                {
                    "id": "playlistId",
                    "title": "title.simpleText",
                    "desc": ["stats.0.runs", "text"],
                    "owner": {
                        "id": "ownerEndpoint.browseEndpoint.browseId",
                        "handle": "ownerEndpoint.browseEndpoint.canonicalBaseUrl",
                        "name": "ownerText.runs.0.text",
                    },
                },
            ],
            "items": [
                (
                    "contents.twoColumnBrowseResultsRenderer.tabs.0"
                    ".tabRenderer.content.sectionListRenderer.contents.0"
                    ".itemSectionRenderer.contents.0.playlistVideoListRenderer.contents"
                ),
                [
                    "playlistVideoRenderer",
                    {
                        "id": "videoId",
                        "title": "title.runs.0.text",
                        "duration": "lengthSeconds",
                        "thumbnail": "thumbnail.thumbnails.0.url",
                        "desc": ["videoInfo.runs", "text"],
                    },
                ],
            ],
        }
    ]

    metadata = playlist["metadata"]
    metadata["desc"] = "".join(metadata["desc"])

    for item in playlist["items"]:
        item["desc"] = "".join(item["desc"])

    return playlist

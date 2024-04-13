from flask import Blueprint, request, abort

from utils import Getter
from youtube.extensions import httpx

bp = Blueprint("video", __name__)


@bp.get("/")
def index():
    id = request.args.get("id") or abort(400)

    httpx.Referer = f"https://www.youtube.com/watch?v={id}"
    data = httpx.player(id)

    video, adaptive_formats, formats = Getter(data)[
        [
            "videoDetails",
            {
                "id": "videoId",
                "title": "title",
                "duration": "lengthSeconds",
                "thumbnail": "thumbnail.thumbnails.0.url",
                "desc": "shortDescription",
                "keywords": "keywords",
                "stat": {
                    "view": "viewCount",
                },
                "owner": {"id": "channelId", "name": "author"},
            },
        ],
        "streamingData.adaptiveFormats",
        "streamingData.formats",
    ]

    video["streams"] = Getter([*adaptive_formats, *formats])[
        {
            "itag": "itag",
            "quality": "qualityLabel",
            "mimetype": "mimeType",
            "content_length": "contentLength",
            "url": "url",
        }
    ]

    return video

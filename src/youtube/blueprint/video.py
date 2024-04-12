from flask import Blueprint, request, abort

from utils import Getter
from youtube.extensions import httpx

bp = Blueprint("video", __name__)


@bp.get("/")
def index():
    id = request.args.get("id") or abort(400)

    httpx.Referer = f"https://www.youtube.com/watch?v={id}"
    res = httpx.post("/youtubei/v1/player", json={"videoId": id})

    video, stream = Getter(res.json())[
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
        [
            "streamingData.adaptiveFormats",
            {"url": "url", "quality": "qualityLabel", "mimetype": "mimeType"},
        ],
    ]

    video["stream"] = stream

    return video

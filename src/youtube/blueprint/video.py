import re

from flask import Blueprint, request, abort, g

from core import Httpx
from utils import Getter
from youtube.extensions import httpx

bp = Blueprint("video", __name__)


@bp.before_request
def before_request():
    g.id = request.args.get("id") or abort(400)


@bp.get("/")
def index():
    httpx.Referer = f"https://www.youtube.com/watch?v={g.id}"
    data = httpx.player(g.id)

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


@bp.get("/stream")
def stream():
    data = {"url": f"https://www.youtube.com/watch?v={g.id}"}
    res = Httpx().post("https://y2nb.com/en/download", data=data)

    RE = re.compile(r'<span class="title">\s*(.*)\s*</span>')
    title = RE.search(res.text)[1]

    RE = re.compile(r'href="(https://.+?\.googlevideo.com/.+?&itag=(\d+).*?)"')
    urls = {m[2]: m[1] for m in RE.finditer(res.text)}

    return {"title": title, "urls": urls}

import re
import json as jsonlib

from flask import Blueprint, request, abort

from utils import Getter
from bilibili.extensions import httpx

bp = Blueprint("video", __name__)
# fmt: off
RE_PAGE_INFO = re.compile(r"<script>\s*window.__INITIAL_STATE__\s*=([^;<]*).*?</script>")
RE_PLAY_INFO = re.compile(r"<script>\s*window.__playinfo__\s*=([^;<]*).*?</script>")
# fmt: on


@bp.get("/")
def index():
    id = request.args.get("id") or abort(400)

    url = f"https://www.bilibili.com/video/{id}"
    res = httpx.get(url)

    parse = lambda p: jsonlib.loads(p.search(res.text).group(1))
    page_info = parse(RE_PAGE_INFO)
    play_info = parse(RE_PLAY_INFO)

    video = Getter(page_info)[{"videoData", "upData", "related"}]
    video["streamData"] = play_info["data"]
    return video

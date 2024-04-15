import os
import time
from glob import glob

from flask import Blueprint, request, abort, send_file

from core import Httpx, huey
from utils import Getter

bp = Blueprint("bing", __name__)
root_dir = os.path.expanduser(f"~/storage/pictures/bing")


@bp.get("/")
def index():
    date = request.args.get("date") or abort(400)
    file = glob(f"{root_dir}/{date[:7]}/[[]{date}]*")[0]
    return send_file(file, "image/webp")


@huey.periodic_task("00 15 *")
def wallpaper():
    httpx = Httpx(base_url="https://www.bing.com")
    res = httpx.get("/hp/api/model", headers={"Cookie": "_EDGE_CD=m=en-us"})

    items = Getter(res.json()["MediaContents"])[
        "FullDateString",
        [
            "ImageContent",
            ("Title", "Image.Url"),
        ],
    ]

    for date, (title, url) in items:
        date = time.strftime("%Y-%m-%d", time.strptime(date, "%b %d, %Y"))
        dirname = f"{root_dir}/{date[:7]}"
        filename = f"{dirname}/[{date}]{title}.webm"

        if not os.path.exists(filename):
            res = httpx.get(url)

            os.makedirs(dirname, exist_ok=True)
            with open(filename, "wb") as fp:
                fp.write(res.content)

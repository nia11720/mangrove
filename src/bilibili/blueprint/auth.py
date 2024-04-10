from time import sleep

from flask import Blueprint, redirect
from httpx import URL

from core import Httpx, huey
from utils import Getter
from bilibili.extensions import httpx as unauthed_httpx, authed_httpx

bp = Blueprint("auth", __name__)

UNAUTH = "bilibili:unauth"
AUTH = "bilibili:auth"

httpx = Httpx(base_url="https://passport.bilibili.com/x/passport-login/web/qrcode")
if not httpx.load_cookies(UNAUTH):
    httpx.head("https://www.bilibili.com/")
    httpx.save_cookies(UNAUTH)
    unauthed_httpx.load_cookies(UNAUTH)


@huey.task()
def check_result(key):
    url = f"/poll?qrcode_key={key}&source=main-fe-header"
    for i in range(30):
        sleep(2)
        res = httpx.get(url)
        data = Getter(res.json()["data"])

        if data["refresh_token"]:
            httpx.save_cookies(AUTH)
            authed_httpx.load_cookies(AUTH)
            break


@bp.get("/qrcode")
def qrcode():
    url = "/generate?source=main-fe-header"
    res = httpx.get(url)
    data = Getter(res.json()["data"])

    url, key = data["url", "qrcode_key"]
    qrcode_api = URL(
        "https://api.qrserver.com/v1/create-qr-code/",
        params={"data": url, "format": "png"},
    )
    check_result(key)

    return redirect(qrcode_api)

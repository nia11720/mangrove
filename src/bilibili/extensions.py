from flask import current_app

from core import Redis, Httpx

redis = Redis(current_app.name)
httpx = Httpx(base_url="https://api.bilibili.com")
authed_httpx = Httpx(base_url="https://api.bilibili.com")

httpx.load_cookies("bilibili:unauth")
authed_httpx.load_cookies("bilibili:auth")

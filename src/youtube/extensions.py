from flask import current_app

from core import Redis, Httpx

redis = Redis(current_app.name)


class YTBHttpx(Httpx):
    def build_request(self, *args, **kwargs):
        kwargs["json"] |= {
            "context": {
                "client": {
                    "clientName": "WEB",
                    "clientVersion": "2.20240410.01.00",
                },
            },
        }

        return super().build_request(*args, **kwargs)


httpx = YTBHttpx(base_url="https://www.youtube.com")

httpx.load_cookies("bilibili:unauth")
if not httpx.load_cookies("bilibili:unauth"):
    httpx.head("/")
    httpx.save_cookies("bilibili:unauth")

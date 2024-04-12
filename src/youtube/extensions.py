from flask import current_app, request

from core import Redis, Httpx
from utils import Getter

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

    def browse(self, id, items_key, **kwargs):
        continuation = request.args.get("continuation")

        json = {"browseId": id, **kwargs}
        if continuation:
            json["continuation"] = continuation
        res = self.post("/youtubei/v1/browse", json=json)

        if continuation:
            items_key = "onResponseReceivedActions.0.appendContinuationItemsAction.continuationItems"
        raw_data, items = Getter(res.json())[None, items_key]

        if items and items[-1].get("continuationItemRenderer"):
            continuation = Getter(items.pop())[
                "continuationItemRenderer.continuationEndpoint.continuationCommand.token"
            ]
        else:
            continuation = None

        return raw_data, items, continuation


httpx = YTBHttpx(base_url="https://www.youtube.com")

httpx.load_cookies("bilibili:unauth")
if not httpx.load_cookies("bilibili:unauth"):
    httpx.head("/")
    httpx.save_cookies("bilibili:unauth")

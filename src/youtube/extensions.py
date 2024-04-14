from flask import current_app, request

from core import Redis, Httpx
from utils import Getter


class YTBHttpx(Httpx):
    client = {
        "context": {
            "client": {
                "clientName": "WEB",
                "clientVersion": "2.20240410.01.00",
            }
        }
    }

    def player(self, id):
        json = self.client | {"videoId": id}
        res = self.post("/youtubei/v1/player", json=json)
        return res.json()

    def browse(self, id, items_key, **kwargs):
        continuation = request.args.get("continuation")

        json = self.client | {"browseId": id, **kwargs}
        if continuation:
            json["continuation"] = continuation
            items_key = "onResponseReceivedActions.0.appendContinuationItemsAction.continuationItems"

        res = self.post("/youtubei/v1/browse", json=json)
        data, items = Getter(res.json())[None, items_key]

        if items and items[-1].get("continuationItemRenderer"):
            continuation = Getter(items.pop())[
                "continuationItemRenderer.continuationEndpoint.continuationCommand.token"
            ]
        else:
            continuation = None

        return data, items, continuation


redis = Redis(current_app.name)
httpx = YTBHttpx(base_url="https://www.youtube.com")

if not httpx.load_cookies("youtube:unauth"):
    httpx.head("/")
    httpx.save_cookies("youtube:unauth")

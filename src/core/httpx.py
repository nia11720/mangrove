from contextvars import ContextVar
from weakref import WeakKeyDictionary

from httpx import Client

from core.env import USER_AGENT


class LocalProperty:
    def __init__(self, name=""):
        self.var = ContextVar(name)

    @property
    def local(self) -> WeakKeyDictionary:
        if self.var.get(None) is None:
            self.var.set(WeakKeyDictionary())
        return self.var.get()

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        else:
            return self.local.get(obj, None)

    def __set__(self, obj, val):
        self.local[obj] = val

    def __delete__(self, obj):
        self.local.pop(obj, None)


class Httpx(Client):
    Referer = LocalProperty("Referer")

    def __init__(self, *, base_url=""):
        headers = {"User-Agent": USER_AGENT}
        super().__init__(base_url=base_url, follow_redirects=True, headers=headers)

    def build_request(self, *args, **kwargs):
        if referer := self.Referer:
            headers = kwargs.get("headers") or {}
            headers["Referer"] = referer
            kwargs["headers"] = headers
        return super().build_request(*args, **kwargs)

from __future__ import annotations

from contextvars import ContextVar
from weakref import WeakKeyDictionary

from httpx import Client

from .config import USER_AGENT
from .redis import Redis

import typing as t

if t.TYPE_CHECKING:
    from httpx._client import Headers


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
            return self.local.get(obj)

    def __set__(self, obj, val):
        self.local[obj] = val

    def __delete__(self, obj):
        self.local.pop(obj, None)


class Httpx(Client):
    Referer = LocalProperty("Referer")

    redis = Redis("cookie")

    def __init__(self, *, base_url=""):
        headers = {"User-Agent": USER_AGENT}
        super().__init__(base_url=base_url, follow_redirects=True, headers=headers)

    def build_request(self, *args, **kwargs):
        if referer := self.Referer:
            headers = kwargs.get("headers") or {}
            headers["Referer"] = referer
            kwargs["headers"] = headers
        return super().build_request(*args, **kwargs)

    @t.overload
    def stream(
        self,
        method: str,
        url: str,
        *,
        params=None,
        headers=None,
        content=None,
        data=None,
        files=None,
        json=None,
    ) -> t.Generator[t.Tuple[int, Headers] | bytes, None, None]: ...

    def stream(self, *args, **kwargs):
        with super().stream(*args, **kwargs) as res:
            yield res.status_code, res.headers
            yield from res.stream

    def save_cookies(self, key: str, max_age=None):
        jar = self.cookies.jar
        with jar._cookies_lock:
            cookies = jar._cookies.copy()

        self.redis.set(key, cookies, pickle=True, ex=max_age)

    def load_cookies(self, key: str):
        cookies = self.redis.get(key, pickle=True)

        if cookies:
            jar = self.cookies.jar
            with jar._cookies_lock:
                jar._cookies = cookies
            return True
        return False

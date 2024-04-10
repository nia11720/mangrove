from threading import Thread
from queue import Queue

import pytest
from flask import Flask, request
from httpx import WSGITransport

from core.httpx import LocalProperty, Httpx


@pytest.fixture
def httpx():
    app = Flask("test")

    @app.get("/")
    def index():
        return "index"

    @app.get("/referer")
    def referer():
        return request.headers.get("Referer", "unset")

    httpx = Httpx(base_url="http://localhost")
    httpx._transport = WSGITransport(app)
    return httpx


@pytest.fixture
def q():
    return Queue()


def test_local_property(q):
    class T:
        x = LocalProperty("x")

    a = T()
    b = T()
    a.x = 1
    assert a.x == 1
    assert T.x.local[a] == 1
    b.x = 2
    assert T.x.local[b] == 2
    del a.x
    assert a not in T.x.local
    del b
    assert len(T.x.local) == 0

    def task():
        a.x = 10
        q.put(T.x.local[a])

    Thread(target=task).start()
    assert q.get() == 10
    assert len(T.x.local) == 0


def test_referer(httpx, q):
    def task(referer=None):
        if referer:
            httpx.Referer = referer
        res = httpx.get("/referer")
        q.put(res.text)

    task("1")
    assert q.get() == "1"
    task()
    assert q.get() == "1"

    Thread(target=task, args=("1",)).start()
    assert q.get() == "1"
    Thread(target=task).start()
    assert q.get() == "unset"


def test_stream(httpx):
    stream = httpx.stream("GET", "/")

    status_code, headers = next(stream)
    assert status_code == 200
    assert headers.get("Content-Length") == "5"

    body = b""
    for chunk in stream:
        body += chunk
    assert body == b"index"

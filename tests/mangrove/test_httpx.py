from threading import Thread
from queue import Queue

import pytest
from httpx import WSGITransport

from core.httpx import LocalProperty, Httpx
from mangrove import app


@pytest.fixture
def httpx():
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
    b.x = 2

    assert T.x.local == {a: 1, b: 2}
    del a.x
    assert T.x.local == {b: 2}
    del b
    assert T.x.local == {}

    def task():
        a.x = 10
        q.put(T.x.local[a])

    Thread(target=task).start()
    assert q.get() == 10
    assert T.x.local == {}


def test_redirect(httpx):
    assert httpx.get("/demo2").text == "demo2"


def test_referer(httpx, q):
    def task(referer=None):
        if referer is not None:
            httpx.Referer = referer
        res = httpx.get("/demo2/referer")
        q.put(res.text)

    task("1")
    assert q.get() == "1"
    task()
    assert q.get() == "1"

    Thread(target=task, args=("1",)).start()
    assert q.get() == "1"
    Thread(target=task).start()
    assert q.get() == "no-referer"

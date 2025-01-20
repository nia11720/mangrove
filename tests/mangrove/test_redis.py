import time
from threading import Thread

import pytest

from core import Redis

r = Redis(db=15)


@pytest.fixture(autouse=True, scope="module")
def reset():
    with r.pipeline() as pipe:
        pipe.delete(
            "demo3:test_string", "demo3:test_hash", "demo3:test_list", "demo3:messages"
        )
        pipe.set("demo3:test_string", "qwert")
        pipe.hset("demo3:test_hash", mapping=dict(k1="111", k2="222"))
        pipe.rpush("demo3:test_list", "qwe", "asd", "zxc")
        pipe.execute()


def test_index(httpx):
    data = httpx.get("/demo3").json()
    assert data["demo3:test_string"] == "qwert"
    assert data["demo3:test_hash"] == {"k1": "111", "k2": "222"}
    assert data["demo3:test_list"] == ["qwe", "asd", "zxc"]


def test_touch(httpx):
    atime = r.get("demo3:atime")
    httpx.post("/demo3/touch")
    assert r.get("demo3:atime") != atime


def test_invalid_message(httpx):
    assert httpx.post("/demo3/publish").status_code == 415
    assert httpx.post("/demo3/publish", json={}).status_code == 400
    assert httpx.post("/demo3/publish", json={"message": ""}).status_code == 400
    assert httpx.post("/demo3/publish", json={"message": 123}).status_code == 400
    assert httpx.post("/demo3/publish", json={"message": []}).status_code == 400
    assert httpx.post("/demo3/publish", json={"message": {}}).status_code == 400
    assert r.llen("demo3:messages") == 0


def test_message(httpx):
    for i in range(25):
        httpx.post("/demo3/publish", json={"message": f"msg - {i}"})
    assert r.llen("demo3:messages") == 20
    assert r.lindex("demo3:messages", 0) == "msg - 24"
    assert r.lindex("demo3:messages", 19) == "msg - 5"

    httpx.post("/demo3/clear")
    assert r.llen("demo3:messages") == 0


def test_pubsub(httpx):
    def task():
        time.sleep(0.5)
        httpx.post("/demo3/publish", json={"message": "channel"})
        httpx.post("/demo3/clear")

    Thread(target=task).start()
    with r.pubsub() as pubsub:
        pubsub.subscribe("demo3:ch")
        for message in pubsub.listen():
            if message["type"] == "message":
                assert message["data"] == "channel"
                break

    Thread(target=task).start()
    with httpx.stream("GET", "/demo3/subscribe") as res:
        for byte in res.stream:
            assert byte == b"data: channel\n\n"
            break

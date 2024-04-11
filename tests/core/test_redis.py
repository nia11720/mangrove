import json as jsonlib
import pickle

import pytest

from core.redis import Redis


@pytest.fixture
def r():
    return Redis("test")


def test_add_prefix(r):
    r.set("s", 1, ex=5)
    assert "@mangrove:test:s" in r.keys("*")
    r.set("@s", 2, ex=5)
    assert "@s" in r.keys("@*")


def test_json_value(r):
    j = {"x": 1}
    r.set("j", j, json=True, ex=5)
    assert r.get("j") == jsonlib.dumps(j, separators=(",", ":"))
    assert r.get("j", json=True) == j


def test_pickle_value(r):
    p = {"x": 1}
    r.set("p", p, pickle=True, ex=50)
    assert r.execute_command("GET", "p", NEVER_DECODE=True) == pickle.dumps(p)
    assert r.get("p", pickle=True) == p


def test_pipeline(r):
    with r.pipeline() as p:
        p.hset("h", "a", 1)
        p.hset("h", "b", 2)
        p.expire("h", 5)
        p.execute()
    assert r.hgetall("h") == {"a": "1", "b": "2"}


def test_pubsub(r):
    with r.pubsub() as c:
        c.psubscribe("ch:x.*")
        msg = c.get_message(timeout=1)
        assert msg["channel"] == "@mangrove:test:ch:x.*"
        r.publish("ch:x.a", "aa")
        msg = c.get_message(timeout=1)
        assert msg["data"] == "aa"

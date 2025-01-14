import pytest

from mangrove import app


@pytest.fixture
def client():
    return app.test_client()


def test_subapp(client):
    assert client.get("/").text == "mangrove"
    assert client.get("/subapp/").text == "subapp"
    assert client.get("/subapp/subapp2/").text == "subapp2"


def test_json(client):
    assert "中文" in client.get("/demo1/text").text
    assert client.get("/demo1/date").json == ["2024-01-01 12:00:00+08:00"]

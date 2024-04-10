from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from core.flask import Flask


@pytest.fixture
def app():
    return Flask("test")


@pytest.fixture
def client(app: Flask):
    return app.test_client()


def test_json_not_ensure_ascii(app, client):
    @app.get("/json")
    def json():
        return ["中文"]

    res = client.get("/json")
    assert "中文" in res.text


@pytest.mark.parametrize("tzname", ["Pacific/Kwajalein", "America/Los_Angeles"])
def test_json_include_datetime(app, client, tzname):
    d = datetime.fromisoformat("2024-01-01 12:00:00")

    @app.get("/json")
    def json():
        return [d.astimezone(ZoneInfo(tzname))]

    res = client.get("/json")
    assert res.json[0] == f"{d.astimezone()}"


def test_sub_app(app, client):
    sub = Flask("test2")

    @sub.get("/")
    def index():
        return "index"

    app.register_flask(sub, url_prefix="/x")
    assert app.config["APPLICATION_ROOT"] == "/"
    assert sub.config["APPLICATION_ROOT"] == "/x"

    res = client.get("/x/")
    assert res.text == "index"

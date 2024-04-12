from bilibili import app

id = "BV1aC41157UM"
client = app.test_client()


def test_video():
    res = client.get(f"/video/?id={id}")
    assert res.status_code == 200

    res = client.get(f"/video/stream?id={id}")
    assert res.status_code == 200

    res = client.get(f"/video/comment?id={id}")
    assert res.status_code == 200

    offset = res.json["cursor"]["pagination_reply"]["next_offset"]
    root = res.json["replies"][0]["rpid"]

    res = client.get(f"/video/comment?id={id}&offset={offset}")
    assert res.status_code == 200

    res = client.get(f"/video/reply?id={id}&root={root}")
    assert res.status_code == 200

    res = client.get(f"/video/reply?id={id}&root={root}&pn=2")
    assert res.status_code == 200

    res = client.get(f"/video/danmaku?id={id}")
    assert res.is_json

    res = client.get(f"/video/danmaku?id={id}&seg=2")
    assert res.is_json

from youtube import app

client = app.test_client()


def test_video():
    id = "n2fn0sb7al8"
    res = client.get(f"/video/?id={id}")
    assert res.status_code == 200


def test_playlist():
    id = "PLKMAC3SlKGwWvn0h_JEFSmjzEBx0lbELs"
    res = client.get(f"/playlist/?id={id}")
    assert res.status_code == 200

    continuation = res.json["continuation"]
    res = client.get(f"/playlist/?id={id}&continuation={continuation}")
    assert res.status_code == 200

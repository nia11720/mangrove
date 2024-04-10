import pytest

from utils.getter import Getter


def test_str_key():
    data = {"x": 1, "y": {"a": 2}}
    getter = Getter(data)

    assert getter["x"] == 1
    assert getter["y"] == {"a": 2}
    assert getter["y.a"] == 2
    assert getter["z"] is None
    with pytest.raises(KeyError):
        getter["z.a"]


def test_sep():
    data = {"x": 1, "y": {"a": 2}}
    getter = Getter(data, sep=":")
    assert getter["y:a"] == 2


def test_tuple_key():
    data = {"x": 1, "y": {"a": 2}}
    getter = Getter(data)

    assert getter["x",] == [1]
    assert getter["x", "y.a"] == [1, 2]


def test_set_key():
    data = {"x": 1, "y": {"a": 2}}
    getter = Getter(data)

    assert getter[{"x"}] == {"x": 1}
    assert getter[{"x", "y"}] == {"x": 1, "y": {"a": 2}}


def test_dict_key():
    data = {"d": {"x": 1, "y": {"a": 2}}}
    getter = Getter(data)

    assert getter[{"q": "d.x", "w": "d.y.a"}] == {"q": 1, "w": 2}
    assert getter[{"_": "d", "q": "x", "w": "y.a"}] == {"q": 1, "w": 2}
    assert getter[{"_d": "d", "q": "x", "_": None, "w": "d.y.a"}] == {"q": 1, "w": 2}


def test_list_data():
    data = [{"x": 1, "y": 2}, {"x": 11, "y": 12}]
    getter = Getter(data)

    assert getter["x"] == [1, 11]
    assert getter["x", "y"] == [[1, 2], [11, 12]]
    assert getter[{"q": "x"}] == [{"q": 1}, {"q": 11}]

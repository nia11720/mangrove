import pytest

from utils.getter import Getter


def test_str_key():
    data = {"x": 1, "y": {"a": 2}, "z": [3]}
    getter = Getter(data)

    assert getter["x"] == 1
    assert getter["y"] == {"a": 2}
    assert getter["y.a"] == 2
    assert getter["z.0"] == 3
    assert getter["null"] is None
    with pytest.raises(KeyError):
        getter["null.a"]


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
    assert getter[{"q": "d.x", "w": ("d.y.a",)}] == {"q": 1, "w": [2]}


def test_list_key():
    data = {"d": {"x": 1, "y": [2]}}
    getter = Getter(data)

    assert getter.get(["d", "y.0"]) == 2
    assert getter.get(["d", "y", None]) == [2]
    assert getter.get(["d", ("y.0",)]) == [2]


def test_list_data():
    data = [{"x": 1, "y": 2}, {"x": 11, "y": 12}]
    getter = Getter(data)

    assert getter["x"] == [1, 11]
    assert getter["x", "y"] == [[1, 2], [11, 12]]
    assert getter[{"q": "x"}] == [{"q": 1}, {"q": 11}]

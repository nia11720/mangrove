import pytest

from httpx import WSGITransport

from core.httpx import Httpx
from mangrove import app


@pytest.fixture
def httpx():
    httpx = Httpx(base_url="http://localhost")
    httpx._transport = WSGITransport(app)
    return httpx

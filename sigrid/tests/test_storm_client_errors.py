import httpx
import pytest

from app.main import StormClient, StormAPIError


class DummyResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


def test_answer_raises_on_non_200(monkeypatch):
    monkeypatch.setenv("STORM_API_KEY", "k")
    monkeypatch.setenv("STORM_API_URL", "https://storm.example")

    def fake_post(url, *, headers=None, json=None, timeout=None):  # type: ignore[no-redef]
        return DummyResponse(500, {"status": "error", "message": "boom"})

    monkeypatch.setattr(httpx, "post", fake_post)

    client = StormClient()
    with pytest.raises(StormAPIError) as ei:
        client.answer("Q")
    assert "500" in str(ei.value)


def test_search_context_wraps_request_error(monkeypatch):
    monkeypatch.setenv("STORM_API_KEY", "k")
    monkeypatch.setenv("STORM_API_URL", "https://storm.example")

    def fake_post(url, *, headers=None, json=None, timeout=None):  # type: ignore[no-redef]
        raise httpx.RequestError("network down")

    monkeypatch.setattr(httpx, "post", fake_post)

    client = StormClient()
    with pytest.raises(StormAPIError) as ei:
        client.search_context("Q2")
    assert "network" in str(ei.value).lower()


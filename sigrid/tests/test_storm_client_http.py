import json
from types import SimpleNamespace

import httpx
import pytest

from app.main import StormClient


class DummyResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self):  # noqa: D401
        return self._payload


def test_stormclient_answer_posts_correct_payload_and_headers(monkeypatch):
    monkeypatch.setenv("STORM_API_KEY", "k-123")
    monkeypatch.setenv("STORM_API_URL", "https://storm.example")

    captured = SimpleNamespace(url=None, headers=None, json=None)

    def fake_post(url, *, headers=None, json=None, timeout=None):  # type: ignore[no-redef]
        captured.url = url
        captured.headers = headers
        captured.json = json
        return DummyResponse(200, {"data": {"answer": "hi", "threadId": "t-1"}})

    monkeypatch.setattr(httpx, "post", fake_post)

    client = StormClient()
    result = client.answer("Hello", bucket_ids=["b1"], thread_id="t-1")

    assert result == {"answer": "hi", "threadId": "t-1"}
    assert captured.url == "https://storm.example/api/v2/answer"
    assert captured.headers == {"storm-api-key": "k-123"}
    assert captured.json == {"question": "Hello", "bucketIds": ["b1"], "threadId": "t-1"}


def test_stormclient_search_context_posts_correct_payload(monkeypatch):
    monkeypatch.setenv("STORM_API_KEY", "k-abc")
    monkeypatch.setenv("STORM_API_URL", "https://storm.example")

    captured = SimpleNamespace(url=None, headers=None, json=None)

    def fake_post(url, *, headers=None, json=None, timeout=None):  # type: ignore[no-redef]
        captured.url = url
        captured.headers = headers
        captured.json = json
        return DummyResponse(
            200,
            {
                "status": "success",
                "data": {
                    "contexts": [
                        {
                            "id": "1",
                            "type": "document",
                            "bucketName": "demo",
                            "fileName": "file.pdf",
                            "pageName": "1",
                            "context": "snippet",
                            "referenceIdx": 1,
                        }
                    ]
                },
            },
        )

    monkeypatch.setattr(httpx, "post", fake_post)

    client = StormClient()
    data = client.search_context("Query", bucket_ids=["bkt"], thread_id="th-9")

    assert captured.url == "https://storm.example/api/v2/answer/context"
    assert captured.headers == {"storm-api-key": "k-abc"}
    assert captured.json == {"question": "Query", "bucketIds": ["bkt"], "threadId": "th-9"}
    assert "contexts" in data and isinstance(data["contexts"], list)


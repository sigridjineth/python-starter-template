from typing import Iterator

from fastapi.testclient import TestClient
from app.main import app


from typing import Optional, Tuple, List


class CaptureClient:
    def __init__(self):
        self.captured: Optional[Tuple[str, Optional[List[str]], Optional[str]]] = None

    def answer(self, question, bucket_ids=None, thread_id=None):
        self.captured = (question, bucket_ids, thread_id)
        return {"question": question, "bucketIds": bucket_ids, "threadId": thread_id}

    def search_context(self, question, bucket_ids=None, thread_id=None):
        self.captured = (question, bucket_ids, thread_id)
        return {"contexts": [{"question": question, "bucketIds": bucket_ids, "threadId": thread_id}]}

    def stream_answer(self, question, bucket_ids=None, thread_id=None) -> Iterator[str]:
        # Simulate SSE payload lines
        yield "data: {\"delta\":{\"content\":\"Hello\"}}\n"
        yield "data: {\"delta\":{\"content\":\" world\"}}\n"


def override_factory(instance):  # type: ignore[no-redef]
    def _get():
        return instance
    return _get


def test_answer_route_passes_through_optional_params():
    from app import main as main_module
    stub = CaptureClient()
    main_module.app.dependency_overrides[main_module.get_storm_client] = override_factory(stub)

    client = TestClient(app)
    body = {"question": "Q", "bucketIds": ["b1", "b2"], "threadId": "t-42"}
    r = client.post("/storm/answer", json=body)
    assert r.status_code == 200
    assert r.json() == {"question": "Q", "bucketIds": ["b1", "b2"], "threadId": "t-42"}


def test_context_route_passes_through_optional_params():
    from app import main as main_module
    stub = CaptureClient()
    main_module.app.dependency_overrides[main_module.get_storm_client] = override_factory(stub)

    client = TestClient(app)
    body = {"question": "CQ", "bucketIds": ["z"], "threadId": "th"}
    r = client.post("/storm/answer/context", json=body)
    assert r.status_code == 200
    data = r.json()
    assert data["contexts"][0] == {"question": "CQ", "bucketIds": ["z"], "threadId": "th"}


def test_stream_endpoint_streams_sse_lines():
    from app import main as main_module
    stub = CaptureClient()
    main_module.app.dependency_overrides[main_module.get_storm_client] = override_factory(stub)

    client = TestClient(app)
    body = {"question": "Hi"}
    r = client.post("/storm/answer/stream", json=body)
    assert r.status_code == 200
    assert "text/event-stream" in r.headers.get("content-type", "")
    # Full body available via TestClient buffering
    assert (
        r.text
        == "data: {\"delta\":{\"content\":\"Hello\"}}\n"
        + "data: {\"delta\":{\"content\":\" world\"}}\n"
    )

from fastapi.testclient import TestClient
from app.main import app


class DummyStormClient:
    def answer(self, question: str, bucket_ids: list[str] | None = None, thread_id: str | None = None):
        # Return a fixed, predictable payload for testing
        return {"answer": "hi", "threadId": "t-123"}


def override_get_storm_client():  # type: ignore[no-redef]
    return DummyStormClient()


def test_storm_answer_returns_client_payload(monkeypatch):
    # Override dependency before creating the client to avoid any network calls
    from app import main as main_module

    main_module.app.dependency_overrides[main_module.get_storm_client] = override_get_storm_client

    client = TestClient(app)
    payload = {"question": "Hello"}
    resp = client.post("/storm/answer", json=payload)

    assert resp.status_code == 200
    assert resp.json() == {"answer": "hi", "threadId": "t-123"}


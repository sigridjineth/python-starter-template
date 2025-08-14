from fastapi.testclient import TestClient
from app.main import app


class DummyStormClient:
    def search_context(self, question: str, bucket_ids: list[str] | None = None, thread_id: str | None = None):
        return {
            "contexts": [
                {
                    "id": "1",
                    "bucketName": "demo",
                    "fileName": "a.pdf",
                    "pageName": "1",
                    "context": "snippet",
                    "referenceIdx": 1,
                    "type": "document",
                }
            ]
        }


def override_get_storm_client():  # type: ignore[no-redef]
    return DummyStormClient()


def test_storm_context_returns_client_payload():
    from app import main as main_module

    main_module.app.dependency_overrides[main_module.get_storm_client] = override_get_storm_client

    client = TestClient(app)
    payload = {"question": "Find related"}
    resp = client.post("/storm/answer/context", json=payload)

    assert resp.status_code == 200
    data = resp.json()
    assert "contexts" in data and isinstance(data["contexts"], list)
    assert data["contexts"][0]["bucketName"] == "demo"


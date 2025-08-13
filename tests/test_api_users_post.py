from fastapi.testclient import TestClient


def test_create_user_echoes_payload_fields():
    from my_api.main import app

    client = TestClient(app)
    payload = {"id": 1, "name": "Alice", "email": "alice@example.com"}

    resp = client.post("/users/", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    for key, value in payload.items():
        assert data[key] == value


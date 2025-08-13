from fastapi.testclient import TestClient


def test_get_user_by_id_returns_matching_user():
    from my_api.main import app

    client = TestClient(app)
    payload = {"id": 3, "name": "Cara", "email": "cara@example.com"}
    client.post("/users/", json=payload)

    resp = client.get("/users/3")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == 3
    assert data["name"] == "Cara"
    assert data["email"] == "cara@example.com"


def test_get_user_by_id_returns_404_when_missing():
    from my_api.main import app

    client = TestClient(app)
    resp = client.get("/users/999")
    assert resp.status_code == 404


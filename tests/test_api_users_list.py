from fastapi.testclient import TestClient


def test_list_users_returns_created_users():
    from my_api.main import app

    client = TestClient(app)
    payload = {"id": 2, "name": "Bob", "email": "bob@example.com"}
    client.post("/users/", json=payload)

    resp = client.get("/users/")
    assert resp.status_code == 200
    data = resp.json()

    assert isinstance(data, list)
    assert any(u["id"] == 2 and u["name"] == "Bob" and u["email"] == "bob@example.com" for u in data)


from fastapi.testclient import TestClient
from app.main import app


def test_answer_requires_question_field():
    client = TestClient(app)
    r = client.post("/storm/answer", json={})
    assert r.status_code == 422


def test_answer_bucketids_must_be_list():
    client = TestClient(app)
    r = client.post("/storm/answer", json={"question": "Q", "bucketIds": "not-a-list"})
    assert r.status_code == 422


from fastapi.testclient import TestClient


def test_api_root_returns_welcome_message():
    # Arrange
    from my_api.main import app  # type: ignore[import-not-found]
    client = TestClient(app)

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to My API"}


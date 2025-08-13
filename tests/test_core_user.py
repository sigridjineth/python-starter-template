import pytest


def test_user_greeting_returns_hello_name():
    # Arrange
    from my_core.models import User  # type: ignore[import-not-found]

    # Act
    user = User(id=1, name="Alice", email="alice@example.com")
    greeting = user.greeting()

    # Assert
    assert greeting == "Hello, Alice!"


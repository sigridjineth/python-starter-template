def test_user_can_be_instantiated_with_required_fields():
    from my_core.models import User

    user = User(id=42, name="Bob", email="bob@example.com")

    assert user.id == 42
    assert user.name == "Bob"
    assert user.email == "bob@example.com"


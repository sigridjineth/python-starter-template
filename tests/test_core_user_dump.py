def test_user_model_dump_contains_required_keys():
    from my_core.models import User

    user = User(id=7, name="Cara", email="cara@example.com")
    data = user.model_dump()

    assert set(["id", "name", "email"]).issubset(data.keys())


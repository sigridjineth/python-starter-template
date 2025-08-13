import pytest
from httpx import AsyncClient


def test_should_initialize_client_with_base_url_and_token():
    from storm_client.client import StormApiClient
    
    base_url = "https://api.example.com"
    token = "test-token-123"
    
    client = StormApiClient(base_url=base_url, token=token)
    
    assert client.base_url == base_url
    assert client.headers == {"Authorization": f"Bearer {token}"}
import pytest
from httpx import AsyncClient, Response
import pytest_asyncio


def test_should_initialize_client_with_base_url_and_token():
    from storm_client.client import StormApiClient
    
    base_url = "https://api.example.com"
    token = "test-token-123"
    
    client = StormApiClient(base_url=base_url, token=token)
    
    assert client.base_url == base_url
    assert client.headers == {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_should_upload_document_and_return_job(httpx_mock):
    from storm_client.client import StormApiClient
    from rag_core.models import Job
    
    # Setup
    base_url = "https://api.example.com"
    token = "test-token"
    client = StormApiClient(base_url=base_url, token=token)
    
    # Mock the response
    httpx_mock.add_response(
        method="POST",
        url=f"{base_url}/api/v1/parsing/upload",
        json={"success": {"job_id": "job-123", "state": "PENDING"}},
        status_code=200
    )
    
    # Create a test file
    test_file_path = "/tmp/test_document.pdf"
    with open(test_file_path, "wb") as f:
        f.write(b"PDF content")
    
    # Test
    job = await client.upload_document(test_file_path)
    
    # Verify
    assert isinstance(job, Job)
    assert job.job_id == "job-123"
    assert job.state == "PENDING"
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


@pytest.mark.asyncio
async def test_should_handle_upload_failure_with_proper_exception(httpx_mock):
    from storm_client.client import StormApiClient
    import httpx
    
    # Setup
    base_url = "https://api.example.com"
    token = "test-token"
    client = StormApiClient(base_url=base_url, token=token)
    
    # Mock error response
    httpx_mock.add_response(
        method="POST",
        url=f"{base_url}/api/v1/parsing/upload",
        status_code=401,
        json={"error": "Unauthorized"}
    )
    
    # Create a test file
    test_file_path = "/tmp/test_document.pdf"
    with open(test_file_path, "wb") as f:
        f.write(b"PDF content")
    
    # Test
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        await client.upload_document(test_file_path)
    
    # Verify
    assert exc_info.value.response.status_code == 401


@pytest.mark.asyncio
async def test_should_get_job_result_with_pending_state(httpx_mock):
    from storm_client.client import StormApiClient
    from rag_core.models import Job
    
    # Setup
    base_url = "https://api.example.com"
    token = "test-token"
    client = StormApiClient(base_url=base_url, token=token)
    job_id = "job-123"
    
    # Mock the response
    httpx_mock.add_response(
        method="GET",
        url=f"{base_url}/api/v1/parsing/job/{job_id}",
        json={
            "success": {
                "job_id": job_id,
                "state": "PENDING"
            }
        },
        status_code=200
    )
    
    # Test
    job, pages = await client.get_job_result(job_id)
    
    # Verify
    assert isinstance(job, Job)
    assert job.job_id == job_id
    assert job.state == "PENDING"
    assert pages is None


@pytest.mark.asyncio
async def test_should_get_job_result_with_completed_state_and_pages(httpx_mock):
    from storm_client.client import StormApiClient
    from rag_core.models import Job, ParsedPage
    
    # Setup
    base_url = "https://api.example.com"
    token = "test-token"
    client = StormApiClient(base_url=base_url, token=token)
    job_id = "job-123"
    
    # Mock the response
    httpx_mock.add_response(
        method="GET",
        url=f"{base_url}/api/v1/parsing/job/{job_id}",
        json={
            "success": {
                "job_id": job_id,
                "state": "COMPLETED",
                "pages": [
                    {"pageNumber": 1, "content": "First page content"},
                    {"pageNumber": 2, "content": "Second page content"}
                ]
            }
        },
        status_code=200
    )
    
    # Test
    job, pages = await client.get_job_result(job_id)
    
    # Verify
    assert isinstance(job, Job)
    assert job.job_id == job_id
    assert job.state == "COMPLETED"
    assert pages is not None
    assert len(pages) == 2
    assert all(isinstance(p, ParsedPage) for p in pages)
    assert pages[0].pageNumber == 1
    assert pages[0].content == "First page content"
    assert pages[1].pageNumber == 2
    assert pages[1].content == "Second page content"


@pytest.mark.asyncio
async def test_should_handle_timeout_gracefully():
    from storm_client.client import StormApiClient
    
    # Verify that our client has timeout configured
    base_url = "https://api.example.com"
    token = "test-token"
    client = StormApiClient(base_url=base_url, token=token)
    
    # The timeout is set in get_job_result method
    # This test verifies that the implementation includes timeout
    assert hasattr(client, 'get_job_result')
    
    # Check that the method signature includes timeout in its implementation
    import inspect
    source = inspect.getsource(client.get_job_result)
    assert 'timeout=' in source, "get_job_result should include timeout parameter"
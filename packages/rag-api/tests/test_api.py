import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
import io


def test_should_upload_pdf_and_return_job_immediately(mocker):
    from rag_api.main import app, rag_service
    from rag_core.models import Job
    
    # Mock the service's client
    mock_upload_response = Job(job_id="job-123", state="PENDING")
    mocker.patch.object(rag_service.client, 'upload_document', 
                       new_callable=AsyncMock, return_value=mock_upload_response)
    
    # Mock the background task to not actually run
    mocker.patch.object(rag_service, 'process_document_in_background', new_callable=AsyncMock)
    
    client = TestClient(app)
    
    # Create a test PDF file
    pdf_content = b"PDF test content"
    file = io.BytesIO(pdf_content)
    
    # Test
    response = client.post(
        "/ingest",
        files={"file": ("test.pdf", file, "application/pdf")}
    )
    
    # Verify
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "job-123"
    assert data["state"] == "PENDING"


def test_should_trigger_background_processing_on_upload(mocker):
    from rag_api.main import app, rag_service
    from rag_core.models import Job
    
    # Mock the service's client
    mock_upload_response = Job(job_id="job-123", state="PENDING")
    mocker.patch.object(rag_service.client, 'upload_document', 
                       new_callable=AsyncMock, return_value=mock_upload_response)
    
    # Mock and spy on the background task
    mock_process = mocker.patch.object(rag_service, 'process_document_in_background', 
                                      new_callable=AsyncMock)
    
    client = TestClient(app)
    
    # Create a test PDF file
    pdf_content = b"PDF test content"
    file = io.BytesIO(pdf_content)
    
    # Test
    response = client.post(
        "/ingest",
        files={"file": ("test.pdf", file, "application/pdf")}
    )
    
    # Verify
    assert response.status_code == 200
    # Verify background task was scheduled
    # Note: In TestClient, background tasks run synchronously
    mock_process.assert_called_once()
    args = mock_process.call_args[0]
    assert args[0] == "job-123"  # job_id
    assert len(args[1]) > 0  # document_id (UUID)


def test_should_get_job_status_by_id():
    from rag_api.main import app, rag_service
    
    # Set up job state
    rag_service.jobs["job-123"] = "PROCESSING"
    
    client = TestClient(app)
    
    # Test
    response = client.get("/ingest/status/job-123")
    
    # Verify
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "job-123"
    assert data["state"] == "PROCESSING"


def test_should_return_404_for_unknown_job_id():
    from rag_api.main import app, rag_service
    
    # Clear jobs
    rag_service.jobs.clear()
    
    client = TestClient(app)
    
    # Test
    response = client.get("/ingest/status/unknown-job")
    
    # Verify
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_should_query_via_post_endpoint(mocker):
    from rag_api.main import app, rag_service
    from rag_core.models import FinalAnswer, RetrievedChunk
    
    # Mock the answer_query method
    mock_answer = FinalAnswer(
        query="What is Python?",
        generated_answer="Python is a programming language",
        retrieved_context=[
            RetrievedChunk(
                id="chunk-1",
                document_id="doc-123",
                text="Python is great",
                page_number=1,
                score=0.95
            )
        ]
    )
    mocker.patch.object(rag_service, 'answer_query', 
                       new_callable=AsyncMock, return_value=mock_answer)
    
    client = TestClient(app)
    
    # Test
    response = client.post(
        "/query",
        json={"query": "What is Python?", "top_k": 3}
    )
    
    # Verify
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "What is Python?"
    assert data["generated_answer"] == "Python is a programming language"
    assert len(data["retrieved_context"]) == 1
    assert data["retrieved_context"][0]["score"] == 0.95


def test_should_return_422_for_invalid_query_request():
    from rag_api.main import app
    
    client = TestClient(app)
    
    # Test with missing query field
    response = client.post(
        "/query",
        json={"top_k": 3}  # Missing required "query" field
    )
    
    # Verify
    assert response.status_code == 422
    
    # Test with invalid top_k
    response = client.post(
        "/query",
        json={"query": "test", "top_k": -1}  # Invalid negative top_k
    )
    
    # Verify
    assert response.status_code == 422
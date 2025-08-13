"""Integration tests for the complete RAG pipeline"""
import pytest
from unittest.mock import AsyncMock, MagicMock
import tempfile
import os


@pytest.mark.asyncio
async def test_end_to_end_pdf_upload_poll_and_query():
    """Test the complete flow from upload to query"""
    from rag_api.main import app
    from rag_service.service import RAGService
    from storm_client.client import StormApiClient
    from rag_engine.engine import TxtaiEngine
    from rag_core.models import Job, ParsedPage, QueryRequest
    from fastapi.testclient import TestClient
    
    # Create services
    client = StormApiClient(base_url="http://test", token="test")
    engine = TxtaiEngine()
    service = RAGService(client=client, engine=engine)
    
    # Mock the Storm API responses
    mock_upload_response = Job(job_id="job-123", state="PENDING")
    mock_completed_response = (
        Job(job_id="job-123", state="COMPLETED"),
        [ParsedPage(pageNumber=1, content="Python is a programming language used for data science")]
    )
    
    # Set up the service with mocked client
    service.client.upload_document = AsyncMock(return_value=mock_upload_response)
    service.client.get_job_result = AsyncMock(return_value=mock_completed_response)
    
    # Process document (simulate background task)
    await service.process_document_in_background("job-123", "doc-123")
    
    # Query the indexed documents
    query = QueryRequest(query="What is Python?", top_k=2)
    answer = await service.answer_query(query)
    
    # Verify
    assert answer.query == "What is Python?"
    assert "Python" in answer.generated_answer
    assert len(answer.retrieved_context) > 0
    assert service.jobs["job-123"] == "COMPLETED"


def test_module_imports():
    """Test that all modules can be imported"""
    # Core models
    from rag_core.models import Job, ParsedPage, Chunk, QueryRequest, RetrievedChunk, FinalAnswer
    
    # Storm client
    from storm_client.client import StormApiClient
    
    # RAG engine
    from rag_engine.engine import TxtaiEngine
    
    # RAG service
    from rag_service.service import RAGService
    
    # RAG API
    from rag_api.main import app
    
    # Verify all imports succeeded
    assert Job is not None
    assert StormApiClient is not None
    assert TxtaiEngine is not None
    assert RAGService is not None
    assert app is not None


def test_all_modules_have_tests():
    """Verify each module has its own test suite"""
    import os
    
    modules = ["rag-core", "storm-client", "rag-engine", "rag-service", "rag-api"]
    
    for module in modules:
        test_dir = f"packages/{module}/tests"
        assert os.path.exists(test_dir), f"Test directory missing for {module}"
        
        # Check for test files
        test_files = [f for f in os.listdir(test_dir) if f.startswith("test_") and f.endswith(".py")]
        assert len(test_files) > 0, f"No test files found for {module}"
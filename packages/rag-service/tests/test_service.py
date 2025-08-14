import pytest
import asyncio
import numpy as np
from unittest.mock import patch, AsyncMock, MagicMock
from rag_core.models import ParsedPage, Chunk


def test_should_chunk_pages_into_fixed_size_chunks():
    from rag_service.service import RAGService
    from storm_client.client import StormApiClient
    from rag_engine.engine import VicinityEngine
    from rag_embedder.embedder import OpenAIEmbedder
    
    # Setup
    client = StormApiClient(base_url="http://test", token="test")
    embedder = OpenAIEmbedder()
    engine = VicinityEngine()
    service = RAGService(client=client, embedder=embedder, engine=engine)
    
    # Test data
    pages = [
        ParsedPage(pageNumber=1, content="A" * 1000),  # 1000 chars
        ParsedPage(pageNumber=2, content="B" * 750),   # 750 chars
    ]
    document_id = "doc-123"
    
    # Test chunking with size=500
    chunks = service._chunk_pages(pages, document_id, chunk_size=500, overlap=0)
    
    # Verify
    assert len(chunks) == 4  # 2 chunks from page 1, 2 chunks from page 2
    
    # Check first page chunks
    assert chunks[0].text == "A" * 500
    assert chunks[0].page_number == 1
    assert chunks[0].document_id == document_id
    assert len(chunks[0].id) > 0
    
    assert chunks[1].text == "A" * 500
    assert chunks[1].page_number == 1
    
    # Check second page chunks
    assert chunks[2].text == "B" * 500
    assert chunks[2].page_number == 2
    
    assert chunks[3].text == "B" * 250
    assert chunks[3].page_number == 2


@pytest.mark.asyncio
async def test_should_process_document_in_background_polling():
    from rag_service.service import RAGService
    from storm_client.client import StormApiClient
    from rag_engine.engine import VicinityEngine
    from rag_embedder.embedder import OpenAIEmbedder
    from rag_core.models import Job
    
    # Setup
    client = StormApiClient(base_url="http://test", token="test")
    embedder = OpenAIEmbedder()
    engine = VicinityEngine()
    service = RAGService(client=client, embedder=embedder, engine=engine)
    
    # Mock the client's get_job_result to return different states
    mock_responses = [
        (Job(job_id="job-123", state="PENDING"), None),
        (Job(job_id="job-123", state="PROCESSING"), None),
        (Job(job_id="job-123", state="COMPLETED"), [
            ParsedPage(pageNumber=1, content="Test content"),
        ])
    ]
    
    with patch.object(client, 'get_job_result', new=AsyncMock(side_effect=mock_responses)):
        # Mock embedder to return test chunks and vectors
        test_chunks = [Chunk(id="chunk-1", document_id="doc-123", text="Test content", page_number=1)]
        test_vectors = np.random.rand(1, 128).astype(np.float32)
        with patch.object(embedder, 'embed_chunks', return_value=(test_chunks, test_vectors)):
            with patch.object(engine, 'build_index') as mock_build_index:
                with patch.object(asyncio, 'sleep', return_value=None):  # Speed up test
                    
                    # Test
                    await service.process_document_in_background("job-123", "doc-123")
                    
                    # Verify
                    assert service.jobs["job-123"] == "COMPLETED"
                    assert client.get_job_result.call_count == 3
                    assert mock_build_index.called
                    # Verify chunks and vectors were passed to build_index
                    assert mock_build_index.call_args[0][0] == test_chunks
                    assert np.array_equal(mock_build_index.call_args[0][1], test_vectors)


@pytest.mark.asyncio
async def test_should_handle_failed_job_state():
    from rag_service.service import RAGService
    from storm_client.client import StormApiClient
    from rag_engine.engine import VicinityEngine
    from rag_embedder.embedder import OpenAIEmbedder
    from rag_core.models import Job
    
    # Setup
    client = StormApiClient(base_url="http://test", token="test")
    embedder = OpenAIEmbedder()
    engine = VicinityEngine()
    service = RAGService(client=client, embedder=embedder, engine=engine)
    
    # Mock failed response
    with patch.object(client, 'get_job_result', new=AsyncMock(return_value=(
        Job(job_id="job-123", state="FAILED"), None
    ))):
        with patch.object(engine, 'build_index') as mock_build_index:
            with patch.object(asyncio, 'sleep', return_value=None):
                
                # Test
                await service.process_document_in_background("job-123", "doc-123")
                
                # Verify
                assert service.jobs["job-123"] == "FAILED"
                assert client.get_job_result.call_count == 1
                assert not mock_build_index.called  # Should not index on failure


def test_should_track_job_states_in_memory():
    from rag_service.service import RAGService
    from storm_client.client import StormApiClient
    from rag_engine.engine import VicinityEngine
    from rag_embedder.embedder import OpenAIEmbedder
    
    # Setup
    client = StormApiClient(base_url="http://test", token="test")
    embedder = OpenAIEmbedder()
    engine = VicinityEngine()
    service = RAGService(client=client, embedder=embedder, engine=engine)
    
    # Test
    assert service.jobs == {}
    
    # Track some jobs
    service.jobs["job-1"] = "PENDING"
    service.jobs["job-2"] = "COMPLETED"
    service.jobs["job-3"] = "FAILED"
    
    # Verify
    assert len(service.jobs) == 3
    assert service.jobs["job-1"] == "PENDING"
    assert service.jobs["job-2"] == "COMPLETED"
    assert service.jobs["job-3"] == "FAILED"


@pytest.mark.asyncio
async def test_should_answer_query_with_context():
    from rag_service.service import RAGService
    from storm_client.client import StormApiClient
    from rag_engine.engine import VicinityEngine
    from rag_embedder.embedder import OpenAIEmbedder
    from rag_core.models import QueryRequest, RetrievedChunk
    
    # Setup
    client = StormApiClient(base_url="http://test", token="test")
    embedder = OpenAIEmbedder()
    engine = VicinityEngine()
    service = RAGService(client=client, embedder=embedder, engine=engine)
    
    # Mock search results
    mock_results = [
        RetrievedChunk(
            id="chunk-1",
            document_id="doc-123",
            text="Python is a programming language",
            page_number=1,
            score=0.95
        ),
        RetrievedChunk(
            id="chunk-2",
            document_id="doc-123",
            text="Python is used for data science",
            page_number=2,
            score=0.85
        )
    ]
    engine.search = lambda query_vector, top_k: mock_results
    
    # Mock embedder to return a query vector
    query_vector = np.random.rand(128).astype(np.float32)
    embedder.embed_query = lambda query: query_vector
    
    # Test
    query = QueryRequest(query="What is Python?", top_k=2)
    answer = await service.answer_query(query)
    
    # Verify
    assert answer.query == "What is Python?"
    assert "Python" in answer.generated_answer
    assert len(answer.retrieved_context) == 2
    assert answer.retrieved_context[0].score == 0.95
    assert answer.retrieved_context[1].score == 0.85


@pytest.mark.asyncio
async def test_should_handle_empty_index_gracefully():
    from rag_service.service import RAGService
    from storm_client.client import StormApiClient
    from rag_engine.engine import VicinityEngine
    from rag_embedder.embedder import OpenAIEmbedder
    from rag_core.models import QueryRequest
    
    # Setup
    client = StormApiClient(base_url="http://test", token="test")
    embedder = OpenAIEmbedder()
    engine = VicinityEngine()
    service = RAGService(client=client, embedder=embedder, engine=engine)
    
    # Mock empty search results
    engine.search = lambda query_vector, top_k: []
    
    # Mock embedder to return a query vector
    query_vector = np.random.rand(128).astype(np.float32)
    embedder.embed_query = lambda query: query_vector
    
    # Test
    query = QueryRequest(query="What is Python?")
    answer = await service.answer_query(query)
    
    # Verify
    assert answer.query == "What is Python?"
    assert answer.generated_answer  # Should have some answer even with no context
    assert len(answer.retrieved_context) == 0
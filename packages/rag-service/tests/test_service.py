import pytest
import asyncio
from rag_core.models import ParsedPage, Chunk


def test_should_chunk_pages_into_fixed_size_chunks():
    from rag_service.service import RAGService
    from storm_client.client import StormApiClient
    from rag_engine.engine import TxtaiEngine
    
    # Setup
    client = StormApiClient(base_url="http://test", token="test")
    engine = TxtaiEngine()
    service = RAGService(client=client, engine=engine)
    
    # Test data
    pages = [
        ParsedPage(pageNumber=1, content="A" * 1000),  # 1000 chars
        ParsedPage(pageNumber=2, content="B" * 750),   # 750 chars
    ]
    document_id = "doc-123"
    
    # Test chunking with size=500
    chunks = service._chunk_pages(pages, document_id, size=500)
    
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
async def test_should_process_document_in_background_polling(mocker):
    from rag_service.service import RAGService
    from storm_client.client import StormApiClient
    from rag_engine.engine import TxtaiEngine
    from rag_core.models import Job
    
    # Setup
    client = StormApiClient(base_url="http://test", token="test")
    engine = TxtaiEngine()
    service = RAGService(client=client, engine=engine)
    
    # Mock the client's get_job_result to return different states
    mock_responses = [
        (Job(job_id="job-123", state="PENDING"), None),
        (Job(job_id="job-123", state="PROCESSING"), None),
        (Job(job_id="job-123", state="COMPLETED"), [
            ParsedPage(pageNumber=1, content="Test content"),
        ])
    ]
    
    mocker.patch.object(client, 'get_job_result', side_effect=mock_responses)
    mocker.patch.object(engine, 'index')
    mocker.patch.object(asyncio, 'sleep', return_value=None)  # Speed up test
    
    # Test
    await service.process_document_in_background("job-123", "doc-123")
    
    # Verify
    assert service.jobs["job-123"] == "COMPLETED"
    assert client.get_job_result.call_count == 3
    assert engine.index.called
    # Verify chunks were created and indexed
    indexed_chunks = engine.index.call_args[0][0]
    assert len(indexed_chunks) == 1
    assert indexed_chunks[0].text == "Test content"


@pytest.mark.asyncio
async def test_should_handle_failed_job_state(mocker):
    from rag_service.service import RAGService
    from storm_client.client import StormApiClient
    from rag_engine.engine import TxtaiEngine
    from rag_core.models import Job
    
    # Setup
    client = StormApiClient(base_url="http://test", token="test")
    engine = TxtaiEngine()
    service = RAGService(client=client, engine=engine)
    
    # Mock failed response
    mocker.patch.object(client, 'get_job_result', return_value=(
        Job(job_id="job-123", state="FAILED"), None
    ))
    mocker.patch.object(engine, 'index')
    mocker.patch.object(asyncio, 'sleep', return_value=None)
    
    # Test
    await service.process_document_in_background("job-123", "doc-123")
    
    # Verify
    assert service.jobs["job-123"] == "FAILED"
    assert client.get_job_result.call_count == 1
    assert not engine.index.called  # Should not index on failure


def test_should_track_job_states_in_memory():
    from rag_service.service import RAGService
    from storm_client.client import StormApiClient
    from rag_engine.engine import TxtaiEngine
    
    # Setup
    client = StormApiClient(base_url="http://test", token="test")
    engine = TxtaiEngine()
    service = RAGService(client=client, engine=engine)
    
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
    from rag_engine.engine import TxtaiEngine
    from rag_core.models import QueryRequest, RetrievedChunk
    
    # Setup
    client = StormApiClient(base_url="http://test", token="test")
    engine = TxtaiEngine()
    service = RAGService(client=client, engine=engine)
    
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
    engine.search = lambda query: mock_results
    
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
    from rag_engine.engine import TxtaiEngine
    from rag_core.models import QueryRequest
    
    # Setup
    client = StormApiClient(base_url="http://test", token="test")
    engine = TxtaiEngine()
    service = RAGService(client=client, engine=engine)
    
    # Mock empty search results
    engine.search = lambda query: []
    
    # Test
    query = QueryRequest(query="What is Python?")
    answer = await service.answer_query(query)
    
    # Verify
    assert answer.query == "What is Python?"
    assert "no relevant documents" in answer.generated_answer.lower() or \
           "no context" in answer.generated_answer.lower()
    assert len(answer.retrieved_context) == 0
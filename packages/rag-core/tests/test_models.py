import pytest
from pydantic import ValidationError


def test_should_create_job_with_required_fields():
    from rag_core.models import Job
    
    job = Job(job_id="test-123", state="PENDING")
    
    assert job.job_id == "test-123"
    assert job.state == "PENDING"


def test_should_fail_creating_job_without_required_fields():
    from rag_core.models import Job
    
    with pytest.raises(ValidationError):
        Job()
    
    with pytest.raises(ValidationError):
        Job(job_id="test-123")
    
    with pytest.raises(ValidationError):
        Job(state="PENDING")


def test_should_create_parsed_page_with_page_number_and_content():
    from rag_core.models import ParsedPage
    
    page = ParsedPage(pageNumber=1, content="This is page content")
    
    assert page.pageNumber == 1
    assert page.content == "This is page content"


def test_should_fail_creating_parsed_page_without_required_fields():
    from rag_core.models import ParsedPage
    
    with pytest.raises(ValidationError):
        ParsedPage()
    
    with pytest.raises(ValidationError):
        ParsedPage(pageNumber=1)
    
    with pytest.raises(ValidationError):
        ParsedPage(content="content")


def test_should_create_chunk_with_all_fields():
    from rag_core.models import Chunk
    
    chunk = Chunk(
        id="chunk-001",
        document_id="doc-123",
        text="This is chunk text",
        page_number=1
    )
    
    assert chunk.id == "chunk-001"
    assert chunk.document_id == "doc-123"
    assert chunk.text == "This is chunk text"
    assert chunk.page_number == 1


def test_should_fail_creating_chunk_without_required_fields():
    from rag_core.models import Chunk
    
    with pytest.raises(ValidationError):
        Chunk()
    
    with pytest.raises(ValidationError):
        Chunk(id="chunk-001", document_id="doc-123", text="text")
    
    with pytest.raises(ValidationError):
        Chunk(id="chunk-001", document_id="doc-123", page_number=1)


def test_should_validate_query_request_top_k_positive():
    from rag_core.models import QueryRequest
    
    # Default value should be 3
    query1 = QueryRequest(query="test query")
    assert query1.query == "test query"
    assert query1.top_k == 3
    
    # Explicit positive value
    query2 = QueryRequest(query="test query", top_k=5)
    assert query2.top_k == 5


def test_should_fail_creating_query_request_with_invalid_top_k():
    from rag_core.models import QueryRequest
    
    # Should fail with negative top_k
    with pytest.raises(ValidationError):
        QueryRequest(query="test", top_k=-1)
    
    # Should fail with zero top_k
    with pytest.raises(ValidationError):
        QueryRequest(query="test", top_k=0)
    
    # Should fail without query
    with pytest.raises(ValidationError):
        QueryRequest(top_k=3)


def test_should_create_retrieved_chunk_with_score():
    from rag_core.models import RetrievedChunk
    
    chunk = RetrievedChunk(
        id="chunk-001",
        document_id="doc-123",
        text="This is chunk text",
        page_number=1,
        score=0.95
    )
    
    assert chunk.id == "chunk-001"
    assert chunk.document_id == "doc-123"
    assert chunk.text == "This is chunk text"
    assert chunk.page_number == 1
    assert chunk.score == 0.95


def test_should_inherit_from_chunk():
    from rag_core.models import Chunk, RetrievedChunk
    
    # RetrievedChunk should be a subclass of Chunk
    assert issubclass(RetrievedChunk, Chunk)
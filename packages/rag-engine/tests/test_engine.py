import pytest
from rag_core.models import Chunk, RetrievedChunk


def test_should_initialize_txtai_embeddings():
    from rag_engine.engine import TxtaiEngine
    
    engine = TxtaiEngine()
    
    # Verify engine is initialized
    assert engine is not None
    assert hasattr(engine, 'embeddings')
    
    # Verify embeddings is configured with content=True
    # This enables storing the original text content
    assert engine.embeddings.config.get("content") is True


def test_should_index_chunks():
    from rag_engine.engine import TxtaiEngine
    
    engine = TxtaiEngine()
    
    # Create test chunks
    chunks = [
        Chunk(
            id="chunk-001",
            document_id="doc-123",
            text="This is the first chunk about Python programming",
            page_number=1
        ),
        Chunk(
            id="chunk-002",
            document_id="doc-123",
            text="This is the second chunk about machine learning",
            page_number=2
        ),
        Chunk(
            id="chunk-003",
            document_id="doc-456",
            text="This is about natural language processing",
            page_number=1
        )
    ]
    
    # Index the chunks
    engine.index(chunks)
    
    # Verify chunks are stored
    assert len(engine.chunks_db) == 3
    assert "chunk-001" in engine.chunks_db
    assert "chunk-002" in engine.chunks_db
    assert "chunk-003" in engine.chunks_db
    
    # Verify embeddings has indexed data
    assert len(engine.embeddings.data) == 3


def test_should_search_by_query_text():
    from rag_engine.engine import TxtaiEngine
    from rag_core.models import QueryRequest
    
    engine = TxtaiEngine()
    
    # Create and index test chunks
    chunks = [
        Chunk(
            id="chunk-001",
            document_id="doc-123",
            text="Python is a powerful programming language for data science",
            page_number=1
        ),
        Chunk(
            id="chunk-002",
            document_id="doc-123",
            text="Machine learning algorithms can process large datasets",
            page_number=2
        ),
        Chunk(
            id="chunk-003",
            document_id="doc-456",
            text="Natural language processing helps computers understand human language",
            page_number=1
        )
    ]
    engine.index(chunks)
    
    # Search for "python programming"
    query = QueryRequest(query="python programming", top_k=2)
    results = engine.search(query)
    
    # Verify results
    assert len(results) == 2  # Should return top_k results
    assert all(isinstance(r, RetrievedChunk) for r in results)
    
    # First result should be chunk-001 (contains both "python" and "programming")
    assert results[0].id == "chunk-001"
    assert results[0].score > 0
    assert results[0].text == chunks[0].text


def test_should_return_top_k_results_with_scores():
    from rag_engine.engine import TxtaiEngine
    from rag_core.models import QueryRequest
    
    engine = TxtaiEngine()
    
    # Create and index more chunks
    chunks = [
        Chunk(id=f"chunk-{i:03d}", document_id="doc-123", 
              text=f"Text about topic {i}", page_number=i)
        for i in range(10)
    ]
    chunks[0].text = "Python programming is awesome"
    chunks[1].text = "Python is great for data science"
    chunks[2].text = "Python web development with Django"
    
    engine.index(chunks)
    
    # Search with top_k=3
    query = QueryRequest(query="Python", top_k=3)
    results = engine.search(query)
    
    # Should return exactly 3 results
    assert len(results) == 3
    
    # All results should have scores
    for result in results:
        assert result.score >= 0
        assert result.score <= 1.0
    
    # Results should be sorted by score (descending)
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_should_handle_empty_index_search():
    from rag_engine.engine import TxtaiEngine
    from rag_core.models import QueryRequest
    
    engine = TxtaiEngine()
    
    # Search without indexing anything
    query = QueryRequest(query="Python programming")
    results = engine.search(query)
    
    # Should return empty list
    assert results == []
    assert isinstance(results, list)
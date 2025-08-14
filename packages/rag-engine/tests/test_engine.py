import pytest
import numpy as np
from rag_core.models import Chunk, RetrievedChunk, QueryRequest


def test_should_initialize_vicinity_engine():
    from rag_engine.engine import VicinityEngine
    
    engine = VicinityEngine()
    
    # Verify engine is initialized
    assert engine is not None
    assert engine.vicinity_instance is None  # Not built yet


def test_should_build_index_with_chunks_and_vectors():
    from rag_engine.engine import VicinityEngine
    
    engine = VicinityEngine()
    
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
    
    # Create mock vectors (normally from embedder)
    vectors = np.random.rand(3, 1536).astype(np.float32)
    
    # Build the index
    engine.build_index(chunks, vectors)
    
    # Verify index is built
    assert engine.vicinity_instance is not None


def test_should_search_by_query_vector():
    from rag_engine.engine import VicinityEngine
    
    engine = VicinityEngine()
    
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
    
    # Create mock vectors with controlled similarity
    vectors = np.array([
        [1.0, 0.0, 0.0],  # chunk-001
        [0.0, 1.0, 0.0],  # chunk-002
        [0.0, 0.0, 1.0],  # chunk-003
    ], dtype=np.float32)
    
    engine.build_index(chunks, vectors)
    
    # Search with query vector similar to first chunk
    query_vector = np.array([0.9, 0.1, 0.0], dtype=np.float32)
    results = engine.search(query_vector, top_k=2)
    
    # Verify results
    assert len(results) == 2  # Should return top_k results
    assert all(isinstance(r, RetrievedChunk) for r in results)
    
    # First result should be chunk-001 (most similar to query vector)
    assert results[0].id == "chunk-001"
    assert results[0].score > 0
    assert results[0].text == chunks[0].text


def test_should_return_top_k_results_with_scores():
    from rag_engine.engine import VicinityEngine
    
    engine = VicinityEngine()
    
    # Create and index more chunks
    chunks = [
        Chunk(id=f"chunk-{i:03d}", document_id="doc-123", 
              text=f"Text about topic {i}", page_number=i)
        for i in range(10)
    ]
    
    # Create random vectors
    vectors = np.random.rand(10, 128).astype(np.float32)
    
    engine.build_index(chunks, vectors)
    
    # Search with top_k=3
    query_vector = np.random.rand(128).astype(np.float32)
    results = engine.search(query_vector, top_k=3)
    
    # Should return exactly 3 results
    assert len(results) == 3
    
    # All results should have scores
    for result in results:
        assert result.score >= 0  # Vicinity returns non-negative scores
        assert isinstance(result.score, float)
    
    # Results should be sorted by score (descending)
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_should_handle_empty_index_search():
    from rag_engine.engine import VicinityEngine
    
    engine = VicinityEngine()
    
    # Search without building index
    query_vector = np.random.rand(128).astype(np.float32)
    results = engine.search(query_vector, top_k=5)
    
    # Should return empty list
    assert results == []
    assert isinstance(results, list)
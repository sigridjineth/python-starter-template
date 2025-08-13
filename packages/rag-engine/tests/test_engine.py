import pytest
from rag_core.models import Chunk


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
import pytest


def test_should_initialize_txtai_embeddings():
    from rag_engine.engine import TxtaiEngine
    
    engine = TxtaiEngine()
    
    # Verify engine is initialized
    assert engine is not None
    assert hasattr(engine, 'embeddings')
    
    # Verify embeddings is configured with content=True
    # This enables storing the original text content
    assert engine.embeddings.config.get("content") is True
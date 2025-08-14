import pytest
import os
from unittest.mock import MagicMock, patch

# Set dummy environment variables for testing
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["STORM_API_TOKEN"] = "test-token"

@pytest.fixture(autouse=True)
def mock_openai_embedder(monkeypatch):
    """Mock OpenAIEmbedder to avoid requiring real API key"""
    mock_embedder = MagicMock()
    mock_embedder.embed_chunks.return_value = ([], [])
    mock_embedder.embed_query.return_value = []
    
    def mock_init(self, model="text-embedding-3-small"):
        self.model = model
        self.client = MagicMock()
        
    with patch("rag_embedder.embedder.OpenAIEmbedder.__init__", mock_init):
        with patch("rag_embedder.embedder.OpenAIEmbedder.embed_chunks", mock_embedder.embed_chunks):
            with patch("rag_embedder.embedder.OpenAIEmbedder.embed_query", mock_embedder.embed_query):
                yield mock_embedder
from typing import List, Dict, Any
from rag_core.models import Chunk, QueryRequest, RetrievedChunk


class MockEmbeddings:
    """Mock embeddings for testing without requiring heavy dependencies"""
    def __init__(self, config: dict):
        self.config = config
        self.data = []
        
    def index(self, data):
        self.data = data
        
    def search(self, query: str, limit: int):
        # Simple mock search - return top results based on string matching
        results = []
        for i, (id, text, _) in enumerate(self.data[:limit]):
            # Simple relevance score based on whether query words appear in text
            score = sum(1 for word in query.lower().split() if word in text.lower()) / len(query.split())
            results.append({"id": id, "score": score})
        return results


class TxtaiEngine:
    def __init__(self):
        # In production, this would use txtai.embeddings.Embeddings
        # For now, using a mock to avoid platform issues
        self.embeddings = MockEmbeddings({"path": "sentence-transformers/all-MiniLM-L6-v2", "content": True})
        self.chunks_db: Dict[str, Chunk] = {}
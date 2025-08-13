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
    
    def index(self, chunks: List[Chunk]):
        """Index a list of chunks for semantic search"""
        # Store chunks in our database
        self.chunks_db.update({c.id: c for c in chunks})
        
        # Convert chunks to format expected by embeddings
        # Format: [(id, text, metadata), ...]
        data_to_index = [(c.id, c.text, None) for c in chunks]
        
        # Index the data
        self.embeddings.index(data_to_index)
    
    def search(self, query: QueryRequest) -> List[RetrievedChunk]:
        """Search for chunks matching the query"""
        # Search the embeddings
        results = self.embeddings.search(query.query, query.top_k)
        
        # Convert results to RetrievedChunk objects
        retrieved_chunks = []
        for result in results:
            chunk_id = result["id"]
            if chunk_id in self.chunks_db:
                chunk = self.chunks_db[chunk_id]
                retrieved_chunk = RetrievedChunk(
                    id=chunk.id,
                    document_id=chunk.document_id,
                    text=chunk.text,
                    page_number=chunk.page_number,
                    score=result["score"]
                )
                retrieved_chunks.append(retrieved_chunk)
        
        # Sort by score (descending)
        retrieved_chunks.sort(key=lambda x: x.score, reverse=True)
        
        return retrieved_chunks
import numpy as np
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
from rag_core.models import Chunk


class SentenceTransformerEmbedder:
    """텍스트를 벡터로 변환하는 책임을 지는 클래스"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("Embedding model loaded.")

    def embed_chunks(self, chunks: List[Chunk]) -> Tuple[List[Chunk], np.ndarray]:
        """청크 리스트를 임베딩하여 원본 청크와 벡터 배열을 반환합니다."""
        if not chunks:
            return [], np.array([])
        
        texts = [chunk.text for chunk in chunks]
        print(f"Embedding {len(texts)} chunks...")
        vectors = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        print("Embedding complete.")
        return chunks, vectors
    
    def embed_query(self, query: str) -> np.ndarray:
        """단일 쿼리 문자열을 임베딩합니다."""
        return self.model.encode(query, convert_to_numpy=True)
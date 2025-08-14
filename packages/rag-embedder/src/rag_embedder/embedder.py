import os
import numpy as np
from typing import List, Tuple
from openai import OpenAI
from rag_core.models import Chunk


class OpenAIEmbedder:
    """OpenAI를 사용하여 텍스트를 벡터로 변환하는 클래스"""
    
    def __init__(self, model: str = "text-embedding-3-small"):
        """
        OpenAI embedder 초기화
        
        Args:
            model: 사용할 OpenAI 임베딩 모델
                  - "text-embedding-3-small": 저렴하고 빠른 모델 (1536 차원)
                  - "text-embedding-3-large": 고성능 모델 (3072 차원)
                  - "text-embedding-ada-002": 레거시 모델 (1536 차원)
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
            
        self.client = OpenAI(api_key=api_key)
        self.model = model
        print(f"OpenAI embedder initialized with model: {model}")

    def _embed_texts(self, texts: List[str]) -> np.ndarray:
        """텍스트 리스트를 임베딩합니다."""
        if not texts:
            return np.array([])
            
        # OpenAI API는 한 번에 최대 2048개의 입력을 처리
        batch_size = 2048
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            response = self.client.embeddings.create(
                model=self.model,
                input=batch_texts
            )
            
            # 응답에서 임베딩 벡터 추출
            embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(embeddings)
            
        return np.array(all_embeddings, dtype=np.float32)

    def embed_chunks(self, chunks: List[Chunk]) -> Tuple[List[Chunk], np.ndarray]:
        """청크 리스트를 임베딩하여 원본 청크와 벡터 배열을 반환합니다."""
        if not chunks:
            return [], np.array([])
        
        texts = [chunk.text for chunk in chunks]
        print(f"Embedding {len(texts)} chunks using OpenAI...")
        
        vectors = self._embed_texts(texts)
        
        print(f"Embedding complete. Vector shape: {vectors.shape}")
        return chunks, vectors
    
    def embed_query(self, query: str) -> np.ndarray:
        """단일 쿼리 문자열을 임베딩합니다."""
        vectors = self._embed_texts([query])
        return vectors[0] if len(vectors) > 0 else np.array([])
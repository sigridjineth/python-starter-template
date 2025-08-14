import numpy as np
from typing import List
from vicinity import Vicinity, Backend, Metric
from rag_core.models import Chunk, RetrievedChunk


class VicinityEngine:
    """Vicinity를 사용하여 벡터를 저장하고 검색하는 책임을 지는 클래스"""

    def __init__(self):
        self.vicinity_instance: Vicinity | None = None

    def build_index(self, chunks: List[Chunk], vectors: np.ndarray):
        """계산된 벡터로 vicinity 인덱스를 구축합니다."""
        if vectors.size == 0:
            print("No vectors to index.")
            return

        print(f"Building index with {len(chunks)} chunks using FAISS backend...")
        # from_vectors_and_items는 벡터와 해당 벡터의 원본 아이템을 받아 인덱스를 생성합니다.
        self.vicinity_instance = Vicinity.from_vectors_and_items(
            vectors=vectors.astype(np.float32),  # FAISS는 float32를 요구합니다.
            items=chunks,
            backend_type=Backend.FAISS,
            metric=Metric.COSINE,
        )
        print("Index build complete.")

    def search(self, query_vector: np.ndarray, top_k: int) -> List[RetrievedChunk]:
        """쿼리 벡터로 가장 유사한 청크를 검색합니다."""
        if self.vicinity_instance is None:
            return []

        # query()는 리스트의 리스트를 반환합니다.
        # 외부 리스트는 쿼리별, 내부 리스트는 (item, score) 튜플들입니다.
        results_list = self.vicinity_instance.query(
            query_vector.astype(np.float32), k=top_k
        )

        if not results_list or not results_list[0]:
            return []

        # 첫 번째 쿼리의 결과만 사용 (단일 쿼리이므로)
        results = results_list[0]

        return [
            RetrievedChunk(**chunk.model_dump(), score=float(score))
            for chunk, score in results
        ]

import asyncio
import uuid
from typing import List
from rag_core.models import Chunk, QueryRequest, FinalAnswer, ParsedPage
from storm_client.client import StormApiClient
from rag_embedder.embedder import SentenceTransformerEmbedder
from rag_engine.engine import VicinityEngine


class RAGService:
    """모든 모듈을 조립하여 RAG 파이프라인을 실행하는 서비스"""

    def __init__(
        self,
        client: StormApiClient,
        embedder: SentenceTransformerEmbedder,
        engine: VicinityEngine,
    ):
        self.client = client
        self.embedder = embedder
        self.engine = engine
        self.jobs = {}  # 인메모리 작업 상태 추적용

    def _chunk_pages(
        self, pages: List[ParsedPage], document_id: str, chunk_size=1000, overlap=100
    ) -> List[Chunk]:
        """파싱된 페이지를 텍스트 청크로 분할합니다."""
        all_chunks = []
        for page in pages:
            content = page.content
            for i in range(0, len(content), chunk_size - overlap):
                all_chunks.append(
                    Chunk(
                        id=str(uuid.uuid4()),
                        document_id=document_id,
                        text=content[i : i + chunk_size],
                        page_number=page.pageNumber,
                    )
                )
        return all_chunks

    async def process_document_in_background(self, job_id: str, document_id: str):
        """백그라운드에서 실행될 작업 폴링, 청킹, 임베딩, 인덱싱 파이프라인"""
        print(f"Starting background processing for job: {job_id}")
        while True:
            try:
                job, pages = await self.client.get_job_result(job_id)
                self.jobs[job_id] = job.state
                print(f"Polling job {job_id}, current state: {job.state}")

                if job.state == "COMPLETED":
                    # 1. Chunking
                    chunks = self._chunk_pages(pages, document_id)
                    # 2. Embedding
                    chunks, vectors = self.embedder.embed_chunks(chunks)
                    # 3. Indexing
                    self.engine.build_index(chunks, vectors)
                    print(f"Job {job_id} completed successfully.")
                    break
                elif job.state in ["FAILED", "ERROR"]:
                    print(f"Job {job_id} failed.")
                    break

                await asyncio.sleep(5)  # 5초 간격으로 폴링
            except Exception as e:
                print(f"Error processing job {job_id}: {e}")
                self.jobs[job_id] = "ERROR"
                break

    async def answer_query(self, query: QueryRequest) -> FinalAnswer:
        """사용자 질문에 대해 답변을 생성합니다."""
        # 1. 쿼리 임베딩
        query_vector = self.embedder.embed_query(query.query)

        # 2. 유사도 검색
        retrieved_context = self.engine.search(query_vector, query.top_k)

        # 3. 답변 생성 (간단한 조합)
        context_str = "\n\n---\n\n".join([c.text for c in retrieved_context])
        generated_answer = f"Based on the retrieved context, here is the relevant information for '{query.query}':\n\n{context_str}"

        return FinalAnswer(
            query=query.query,
            generated_answer=generated_answer,
            retrieved_context=retrieved_context,
        )

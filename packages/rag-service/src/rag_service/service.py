import asyncio
import uuid
from typing import List, Dict
from rag_core.models import Chunk, QueryRequest, FinalAnswer, ParsedPage
from storm_client.client import StormApiClient
from rag_engine.engine import TxtaiEngine


class RAGService:
    def __init__(self, client: StormApiClient, engine: TxtaiEngine):
        self.client = client
        self.engine = engine
        self.jobs: Dict[str, str] = {}  # job_id -> state mapping
        
    def _chunk_pages(self, pages: List[ParsedPage], document_id: str, size: int = 500) -> List[Chunk]:
        """Split pages into fixed-size chunks"""
        all_chunks = []
        
        for page in pages:
            content = page.content
            page_number = page.pageNumber
            
            # Split content into chunks of specified size
            for i in range(0, len(content), size):
                chunk = Chunk(
                    id=str(uuid.uuid4()),
                    document_id=document_id,
                    text=content[i:i+size],
                    page_number=page_number
                )
                all_chunks.append(chunk)
                
        return all_chunks
    
    async def process_document_in_background(self, job_id: str, document_id: str):
        """Poll job status and index document when completed"""
        while True:
            job, pages = await self.client.get_job_result(job_id)
            self.jobs[job_id] = job.state
            
            if job.state == "COMPLETED":
                # Chunk the pages and index them
                chunks = self._chunk_pages(pages, document_id)
                self.engine.index(chunks)
                print(f"Job {job_id} completed and indexed {len(chunks)} chunks.")
                break
            elif job.state in ["FAILED", "ERROR"]:
                print(f"Job {job_id} failed.")
                break
                
            # Poll every 5 seconds
            await asyncio.sleep(5)
    
    async def answer_query(self, query: QueryRequest) -> FinalAnswer:
        """Answer a query using the indexed documents"""
        # Search for relevant chunks
        retrieved_context = self.engine.search(query)
        
        # Generate answer based on context
        if retrieved_context:
            # Concatenate context texts
            context_str = "\n".join([chunk.text for chunk in retrieved_context[:3]])
            # Simple answer synthesis (in production, would use LLM)
            generated_answer = f"Based on the documents: {context_str[:200]}..."
        else:
            generated_answer = "No relevant documents found to answer your query."
        
        return FinalAnswer(
            query=query.query,
            generated_answer=generated_answer,
            retrieved_context=retrieved_context
        )
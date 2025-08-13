from pydantic import BaseModel, Field
from typing import List


class Job(BaseModel):
    job_id: str
    state: str


class ParsedPage(BaseModel):
    pageNumber: int
    content: str


class Chunk(BaseModel):
    id: str
    document_id: str
    text: str
    page_number: int


class QueryRequest(BaseModel):
    query: str
    top_k: int = Field(default=3, gt=0)


class RetrievedChunk(Chunk):
    score: float


class FinalAnswer(BaseModel):
    query: str
    generated_answer: str
    retrieved_context: List[RetrievedChunk]
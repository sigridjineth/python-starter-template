from pydantic import BaseModel


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
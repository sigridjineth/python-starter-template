from pydantic import BaseModel


class Job(BaseModel):
    job_id: str
    state: str


class ParsedPage(BaseModel):
    pageNumber: int
    content: str
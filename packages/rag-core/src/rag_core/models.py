from pydantic import BaseModel


class Job(BaseModel):
    job_id: str
    state: str
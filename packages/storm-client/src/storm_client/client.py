import httpx
from typing import List, Optional
from rag_core.models import Job, ParsedPage


class StormApiClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}

    async def upload_document(self, file_path: str) -> Job:
        async with httpx.AsyncClient() as client:
            with open(file_path, "rb") as f:
                files = {"file": (file_path, f, "application/pdf")}
                response = await client.post(
                    f"{self.base_url}/api/v1/parsing/upload",
                    files=files,
                    headers=self.headers,
                )
            response.raise_for_status()
            data = response.json()
            return Job(**data["success"])

    async def get_job_result(
        self, job_id: str
    ) -> tuple[Job, Optional[List[ParsedPage]]]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/parsing/job/{job_id}",
                headers=self.headers,
                timeout=30.0,
            )
        response.raise_for_status()
        data = response.json()["success"]
        job = Job(job_id=data["job_id"], state=data["state"])
        pages = (
            [ParsedPage(**p) for p in data.get("pages", [])]
            if job.state == "COMPLETED"
            else None
        )
        return job, pages

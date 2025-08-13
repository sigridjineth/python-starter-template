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
                    headers=self.headers
                )
            response.raise_for_status()
            data = response.json()
            return Job(**data["success"])
import os
from typing import Any, Iterator
from pydantic import BaseModel

import httpx  # type: ignore[import-not-found]
from fastapi import FastAPI, Depends


class StormClient:
    def __init__(
        self,
        api_key: str | None = None,
        api_url: str | None = None,
        timeout: float = 30.0,
    ):
        key = api_key if api_key is not None else os.getenv("STORM_API_KEY", "")
        url = (
            api_url
            if api_url is not None
            else os.getenv("STORM_API_URL", "https://live-stargate.sionic.im")
        )
        self.api_key: str = key
        self.api_url: str = url
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {"storm-api-key": self.api_key}

    def answer(
        self,
        question: str,
        bucket_ids: list[str] | None = None,
        thread_id: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"question": question}
        if bucket_ids is not None:
            payload["bucketIds"] = bucket_ids
        if thread_id is not None:
            payload["threadId"] = thread_id

        try:
            resp = httpx.post(
                f"{self.api_url}/api/v2/answer",
                headers=self._headers(),
                json=payload,
                timeout=self.timeout,
            )
        except httpx.RequestError as e:  # pragma: no cover - exercised via tests
            raise StormAPIError(f"Request failed: {e}")
        if getattr(resp, "status_code", 200) != 200:
            raise StormAPIError(f"STORM API returned {resp.status_code}")
        raw = resp.json().get("data", {})
        return raw if isinstance(raw, dict) else {}

    def search_context(
        self,
        question: str,
        bucket_ids: list[str] | None = None,
        thread_id: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"question": question}
        if bucket_ids is not None:
            payload["bucketIds"] = bucket_ids
        if thread_id is not None:
            payload["threadId"] = thread_id

        try:
            resp = httpx.post(
                f"{self.api_url}/api/v2/answer/context",
                headers=self._headers(),
                json=payload,
                timeout=self.timeout,
            )
        except httpx.RequestError as e:  # pragma: no cover
            raise StormAPIError(f"Request failed: {e}")
        if getattr(resp, "status_code", 200) != 200:
            raise StormAPIError(f"STORM API returned {resp.status_code}")
        raw = resp.json().get("data", {})
        return raw if isinstance(raw, dict) else {}

    def stream_answer(
        self,
        question: str,
        bucket_ids: list[str] | None = None,
        thread_id: str | None = None,
    ) -> Iterator[str]:
        payload: dict[str, Any] = {"question": question}
        if bucket_ids is not None:
            payload["bucketIds"] = bucket_ids
        if thread_id is not None:
            payload["threadId"] = thread_id

        try:
            with httpx.stream(
                "POST",
                f"{self.api_url}/api/v2/answer/stream",
                headers=self._headers(),
                json=payload,
                timeout=self.timeout,
            ) as r:
                if getattr(r, "status_code", 200) != 200:
                    raise StormAPIError(f"STORM API returned {r.status_code}")
                for line in r.iter_lines():
                    if line is None:
                        continue
                    yield line + "\n"
        except httpx.RequestError as e:  # pragma: no cover
            raise StormAPIError(f"Request failed: {e}")


class StormAPIError(Exception):
    pass


def get_storm_client() -> StormClient:
    return StormClient()


app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello from python-starter-template!"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


class ChatRequest(BaseModel):
    question: str
    bucketIds: list[str] | None = None
    threadId: str | None = None


@app.post("/storm/answer")
def storm_answer(
    payload: ChatRequest, client: StormClient = Depends(get_storm_client)
) -> dict:
    return client.answer(
        payload.question, bucket_ids=payload.bucketIds, thread_id=payload.threadId
    )


@app.post("/storm/answer/context")
def storm_answer_context(
    payload: ChatRequest, client: StormClient = Depends(get_storm_client)
) -> dict:
    return client.search_context(
        payload.question, bucket_ids=payload.bucketIds, thread_id=payload.threadId
    )


@app.post("/storm/answer/stream")
def storm_answer_stream(
    payload: ChatRequest, client: StormClient = Depends(get_storm_client)
) -> Any:
    from fastapi.responses import StreamingResponse

    gen = client.stream_answer(
        payload.question, bucket_ids=payload.bucketIds, thread_id=payload.threadId
    )
    return StreamingResponse(gen, media_type="text/event-stream")

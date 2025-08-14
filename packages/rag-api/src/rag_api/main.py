import os
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from rag_core.models import QueryRequest, FinalAnswer, Job
from rag_service.service import RAGService
from storm_client.client import StormApiClient
from rag_embedder.embedder import OpenAIEmbedder
from rag_engine.engine import VicinityEngine

STORM_API_URL: str = os.getenv(
    "STORM_API_URL", "https://live-storm-apis-parse-router.sionic.im"
)

STORM_API_TOKEN = os.getenv("STORM_API_TOKEN")

UPLOAD_DIR: str = "/tmp/vicinity_rag_uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

client = StormApiClient(base_url=STORM_API_URL, token=STORM_API_TOKEN)
embedder = OpenAIEmbedder()
engine = VicinityEngine()
rag_service = RAGService(client=client, embedder=embedder, engine=engine)

app = FastAPI(
    title="Vicinity-based RAG API",
    description="A modular RAG pipeline using Storm API, OpenAI Embeddings, and Vicinity.",
)


@app.post("/ingest", response_model=Job, status_code=202)
async def ingest_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        job = await rag_service.client.upload_document(file_path)
        rag_service.jobs[job.job_id] = job.state

        background_tasks.add_task(
            rag_service.process_document_in_background, job.job_id, job.job_id
        )

        return job

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start ingestion job: {e}"
        )


@app.get("/ingest/status/{job_id}", response_model=Job)
async def get_job_status(job_id: str):
    state = rag_service.jobs.get(job_id)

    if state is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return Job(job_id=job_id, state=state)


@app.post("/query", response_model=FinalAnswer)
async def ask_question(query: QueryRequest):
    return await rag_service.answer_query(query)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "engine_indexed": rag_service.engine.vicinity_instance is not None,
    }

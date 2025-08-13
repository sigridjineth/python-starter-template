import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from rag_core.models import QueryRequest, FinalAnswer, Job
from rag_service.service import RAGService
from storm_client.client import StormApiClient
from rag_engine.engine import TxtaiEngine

# --- Dependency Injection and Configuration ---
STORM_API_URL = os.getenv(
    "STORM_API_URL", "https://live-storm-apis-parse-router.sionic.im"
)
STORM_API_TOKEN = os.getenv("STORM_API_TOKEN", "demo_Kx8fH9mN2pQrS3vT5wY7zA")
UPLOAD_DIR = "/tmp/api_rag_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize services
client = StormApiClient(base_url=STORM_API_URL, token=STORM_API_TOKEN)
engine = TxtaiEngine()
rag_service = RAGService(client=client, engine=engine)

# Create FastAPI app
app = FastAPI(title="API-Driven RAG Pipeline")


@app.post("/ingest", response_model=Job)
async def ingest_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Uploads a PDF, starts async processing, and returns a job ID immediately."""
    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Upload to Storm API
    document_id = str(uuid.uuid4())
    job = await rag_service.client.upload_document(file_path)
    rag_service.jobs[job.job_id] = job.state

    # Start background processing
    background_tasks.add_task(
        rag_service.process_document_in_background, job.job_id, document_id
    )

    return job


@app.get("/ingest/status/{job_id}", response_model=Job)
async def get_job_status(job_id: str):
    """Check the status of an ingestion job."""
    state = rag_service.jobs.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")
    return Job(job_id=job_id, state=state)


@app.post("/query", response_model=FinalAnswer)
async def ask_question(query: QueryRequest):
    """Query the indexed documents."""
    return await rag_service.answer_query(query)

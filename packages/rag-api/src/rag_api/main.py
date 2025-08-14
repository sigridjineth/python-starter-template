import os
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from rag_core.models import QueryRequest, FinalAnswer, Job
from rag_service.service import RAGService
from storm_client.client import StormApiClient
from rag_embedder.embedder import OpenAIEmbedder
from rag_engine.engine import VicinityEngine

# --- 환경 변수에서 설정 로드 ---
STORM_API_URL = os.getenv(
    "STORM_API_URL", "https://live-storm-apis-parse-router.sionic.im"
)
STORM_API_TOKEN = os.getenv("STORM_API_TOKEN")  # 실제 운영 시에는 반드시 토큰 설정 필요
UPLOAD_DIR = "/tmp/vicinity_rag_uploads"

if not STORM_API_TOKEN:
    print("Warning: STORM_API_TOKEN environment variable not set. Using a demo token.")
    STORM_API_TOKEN = "demo_Kx8fH9mN2pQrS3vT5wY7zA"

# --- 의존성 주입 (DI): 애플리케이션 시작 시 모든 컴포넌트를 한 번만 생성 ---
os.makedirs(UPLOAD_DIR, exist_ok=True)

client = StormApiClient(base_url=STORM_API_URL, token=STORM_API_TOKEN)
embedder = OpenAIEmbedder()
engine = VicinityEngine()
rag_service = RAGService(client=client, embedder=embedder, engine=engine)
# ---

app = FastAPI(
    title="Vicinity-based RAG API",
    description="A modular RAG pipeline using Storm API, OpenAI Embeddings, and Vicinity.",
)


@app.post("/ingest", response_model=Job, status_code=202)
async def ingest_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """PDF 파일을 업로드하고 비동기 처리를 시작합니다. 즉시 작업 ID를 반환합니다."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        job = await rag_service.client.upload_document(file_path)
        rag_service.jobs[job.job_id] = job.state

        # FastAPI의 BackgroundTasks를 사용하여 요청-응답 사이클과 무관하게
        # 무거운 작업을 백그라운드에서 실행합니다.
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
    """수집 작업의 현재 상태를 확인합니다."""
    state = rag_service.jobs.get(job_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return Job(job_id=job_id, state=state)


@app.post("/query", response_model=FinalAnswer)
async def ask_question(query: QueryRequest):
    """인덱싱된 문서를 기반으로 질문에 답변합니다."""
    return await rag_service.answer_query(query)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "engine_indexed": rag_service.engine.vicinity_instance is not None,
    }

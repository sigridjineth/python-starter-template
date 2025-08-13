네, 알겠습니다. `vicinity`를 벡터 검색 엔진으로 사용하고, 각 모듈의 책임을 명확하게 분리하는 RAG 파이프라인 구축 프로젝트를 아주 상세하고 긴 설명과 함께, 모든 코드와 명령어를 포함하여 처음부터 끝까지 따라 할 수 있도록 재구성해 드리겠습니다.

-----

### \#\# 5. 실전 프로젝트: `vicinity` 기반의 분리된 RAG 파이프라인 구축 (상세편)

이번 실전 프로젝트에서는 경량 벡터 스토어 `vicinity`를 핵심 검색 엔진으로 채택하여, 실제 프로덕션 환경에서 볼 수 있는 전문적인 RAG(검색 증강 생성) 애플리케이션을 단계별로 구축합니다. 이 과정은 \*\*텍스트를 벡터로 변환하는 '임베딩'\*\*과 \*\*벡터를 저장하고 검색하는 '인덱싱/서빙'\*\*의 책임을 명확히 분리하는 것을 핵심 교육 목표로 삼습니다.

#### **🎯 교육 목표**

1.  **책임 분리 원칙(SRP) 심화 학습**: 데이터 모델, 외부 API 클라이언트, 텍스트 임베더, 벡터 검색 엔진, 비즈니스 로직, 웹 API 등 각 기능의 책임을 완전히 독립된 모듈로 설계하여, 실제 현업에서 마주할 수 있는 수준의 아키텍처 설계 원칙을 체득합니다.
2.  **`uv` 네이티브 빌드 백엔드 완전 정복**: 모든 프로젝트 모듈에서 `Hatchling`의 복잡성 없이 `uv`의 네이티브 빌드 백엔드만을 사용하여, `pyproject.toml`을 간결하고 통일성 있게 관리하는 방법을 완벽히 이해합니다.
3.  **실용적인 RAG 파이프라인 설계 및 구현**: 외부 API 연동, 비동기 작업 처리, 텍스트 벡터화, 그리고 `vicinity`를 이용한 시맨틱 검색에 이르는 전체 RAG 파이프라인의 흐름을 직접 코드로 구현하며 경험합니다.

-----

### **5.1. 기능 명세 및 최종 아키텍처**

#### **기능 명세**

  * **문서 수집 및 파싱**: 외부 'Storm Parse API'를 호출하여 사용자가 업로드한 PDF 문서를 페이지별 텍스트로 변환합니다.
  * **텍스트 임베딩**: 파싱된 텍스트를 검색에 용이한 작은 단위(Chunk)로 분할하고, `sentence-transformers` 모델을 사용하여 각 청크를 고차원 벡터로 변환합니다.
  * **벡터 인덱싱**: 생성된 벡터와 원본 텍스트 청크를 `vicinity` 라이브러리의 FAISS 백엔드를 사용해 효율적으로 인덱싱합니다.
  * **시맨틱 검색**: 사용자 질문을 실시간으로 벡터화한 뒤, `vicinity` 인덱스 내에서 의미적으로 가장 유사한 텍스트 청크를 신속하게 검색합니다.
  * **답변 생성 및 제공**: 검색된 청크(컨텍스트)를 바탕으로 최종 답변을 구성하여 사용자에게 API를 통해 제공합니다.

#### **모듈 아키텍처 (6-모듈 책임 분리 구조)**

```
vicinity-rag-pipeline/
├── pyproject.toml           # ⭐️ Workspace 루트
├── uv.lock                  # ⭐️ Workspace 전체의 단일 잠금 파일
└── packages/
    ├── rag-core/            # 데이터 모델 (DTOs) 및 공통 정의
    ├── storm-client/        # Storm Parse API와의 통신 전담 (외부 세계와의 관문)
    ├── rag-embedder/        # 텍스트를 벡터로 변환하는 '임베딩' 전담
    ├── rag-engine/          # `vicinity`를 사용해 벡터를 저장/검색하는 '엔진' 전담
    ├── rag-service/         # 위 모듈들을 조립하여 전체 파이프라인을 오케스트레이션
    └── rag-api/             # FastAPI를 통한 외부 사용자 인터페이스
```

-----

### **5.2. 미션 1: 프로젝트 기반 설정 (`rag-core` 모듈)**

**목표**: 파이프라인 전체에서 데이터가 흘러가는 표준 규격(데이터 모델)을 정의하고, `uv` 네이티브 빌드 백엔드의 간결함을 확인합니다.

#### **1. Workspace 루트 및 디렉터리 생성**

```bash
# 프로젝트의 최상위 디렉터리를 생성하고 이동합니다.
mkdir vicinity-rag-pipeline && cd vicinity-rag-pipeline

# uv를 사용하여 이 디렉터리가 패키지 프로젝트의 루트임을 초기화합니다.
uv init --package

# 루트 pyproject.toml 파일을 작성합니다.
# 이 파일은 전체 워크스페이스를 정의하는 역할을 합니다.
cat > pyproject.toml << 'EOF'
[project]
name = "vicinity-rag-pipeline"
version = "0.1.0"
description = "A practical RAG pipeline with uv, vicinity, and FastAPI"
requires-python = ">=3.11"

# [tool.uv.workspace] 테이블은 이 프로젝트가
# 여러 하위 모듈(멤버)을 관리하는 워크스페이스임을 uv에게 알려줍니다.
[tool.uv.workspace]
members = ["packages/*"]
EOF

# 모든 하위 모듈들이 위치할 'packages' 디렉터리를 생성합니다.
mkdir packages
```

#### **2. `rag-core` 패키지 생성 및 설정**

```bash
# 'packages' 디렉터리 내에 'rag-core'라는 새 패키지를 초기화합니다.
uv init packages/rag-core --package --name rag-core

# rag-core 모듈의 pyproject.toml 파일을 작성합니다.
cat > packages/rag-core/pyproject.toml << 'EOF'
[project]
name = "rag-core"
version = "0.1.0"
description = "Core data models for the RAG pipeline"
dependencies = [
    "pydantic>=2.0.0",
]

# 💡 교육 포인트: uv의 네이티브 빌드 백엔드 설정
# hatchling이나 setuptools 같은 외부 빌드 도구가 필요 없습니다.
# uv는 [project]의 name 필드를 보고 빌드할 패키지(rag_core/)를 자동으로 인식합니다.
# 이로 인해 [tool.hatch] 같은 별도 설정이 완전히 사라져 매우 간결합니다.
[build-system]
requires = ["uv>=0.2.0"]
build-backend = "uv.backend"
EOF
```

#### **3. `rag-core` 데이터 모델 코드 작성**

```bash
# 소스 코드를 담을 디렉터리를 생성합니다.
mkdir -p packages/rag-core/rag_core

# 파이프라인의 각 단계에서 사용할 데이터 모델을 정의합니다.
cat > packages/rag-core/rag_core/models.py << 'EOF'
from pydantic import BaseModel, Field
from typing import List, Optional

class Job(BaseModel):
    """Storm API의 작업 상태를 나타내는 모델"""
    job_id: str
    state: str

class ParsedPage(BaseModel):
    """Storm API가 반환하는 파싱된 페이지 데이터"""
    pageNumber: int
    content: str

class Chunk(BaseModel):
    """검색 및 인덱싱의 기본 단위가 되는 텍스트 조각"""
    id: str
    document_id: str
    text: str
    page_number: int

class QueryRequest(BaseModel):
    """사용자의 질문 API 요청을 나타내는 모델"""
    query: str
    top_k: int = Field(default=3, ge=1, le=10)

class RetrievedChunk(Chunk):
    """검색 결과로 반환된 청크 (유사도 점수 포함)"""
    score: float

class FinalAnswer(BaseModel):
    """사용자에게 최종적으로 반환될 답변 모델"""
    query: str
    generated_answer: str
    retrieved_context: List[RetrievedChunk]
EOF
```

-----

### **5.3. 미션 2: 외부 연동 모듈 (`storm-client`)**

**목표**: 외부 API와의 통신 로직을 별도의 모듈로 완벽하게 분리하여, API 명세가 변경되더라도 다른 모듈에 미치는 영향을 최소화하는 방법을 학습합니다.

#### **1. `storm-client` 패키지 생성 및 설정**

```bash
# 'storm-client' 패키지를 초기화합니다.
uv init packages/storm-client --package --name storm-client

# storm-client 모듈의 pyproject.toml 파일을 작성합니다.
cat > packages/storm-client/pyproject.toml << 'EOF'
[project]
name = "storm-client"
version = "0.1.0"
description = "HTTP client for interacting with the Storm Parse API"
dependencies = [
    "rag-core", # API 응답을 담을 모델을 사용하기 위해 의존
    "httpx>=0.27.0", # 비동기 HTTP 요청을 위한 라이브러리
]

[tool.uv.sources]
# 'rag-core'는 PyPI가 아닌 워크스페이스 내부에서 찾도록 지정합니다.
rag-core = { workspace = true }

[build-system]
requires = ["uv>=0.2.0"]
build-backend = "uv.backend"
EOF
```

#### **2. `storm-client` API 클라이언트 코드 작성**

```bash
# 소스 코드를 담을 디렉터리를 생성합니다.
mkdir -p packages/storm-client/storm_client

# Storm Parse API와 통신하는 클라이언트 클래스를 구현합니다.
cat > packages/storm-client/storm_client/client.py << 'EOF'
import httpx
from typing import List, Optional
from rag_core.models import Job, ParsedPage

class StormApiClient:
    """Storm Parse API와의 모든 HTTP 통신을 책임지는 클라이언트"""
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
        # 타임아웃을 설정하여 무한정 기다리는 것을 방지합니다.
        self.timeout = httpx.Timeout(30.0, connect=5.0)

    async def upload_document(self, file_path: str) -> Job:
        """지정된 경로의 파일을 API에 업로드하고 작업 ID를 반환합니다."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            with open(file_path, "rb") as f:
                files = {"file": (file_path, f, "application/pdf")}
                print(f"Uploading {file_path} to Storm API...")
                response = await client.post(
                    f"{self.base_url}/api/v1/parsing/upload",
                    files=files,
                    headers=self.headers
                )
            response.raise_for_status() # 2xx가 아닌 상태 코드에 대해 예외 발생
            data = response.json()
            job = Job(**data["success"])
            print(f"File uploaded successfully. Job ID: {job.job_id}")
            return job

    async def get_job_result(self, job_id: str) -> tuple[Job, Optional[List[ParsedPage]]]:
        """주어진 작업 ID의 상태를 조회하고, 완료 시 파싱된 페이지를 반환합니다."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/parsing/job/{job_id}",
                headers=self.headers,
            )
        response.raise_for_status()
        data = response.json()["success"]
        job = Job(job_id=data["job_id"], state=data["state"])
        
        pages = None
        if job.state == "COMPLETED":
            pages = [ParsedPage(**p) for p in data.get("pages", [])]
        
        return job, pages
EOF
```

-----

### **5.4. 미션 3: `rag-embedder` 및 `rag-engine` 구현**

**목표**: 텍스트를 벡터로 변환하는 '임베딩'의 책임과, 벡터를 저장하고 검색하는 '엔진'의 책임을 명확히 분리하여 각 기술에 독립적인 모듈을 만듭니다.

#### **1. `rag-embedder` 패키지 생성 (텍스트 -\> 벡터 변환)**

```bash
# 'rag-embedder' 패키지를 초기화합니다.
uv init packages/rag-embedder --package --name rag-embedder

# pyproject.toml 파일을 작성합니다.
cat > packages/rag-embedder/pyproject.toml << 'EOF'
[project]
name = "rag-embedder"
version = "0.1.0"
description = "Handles text to vector embedding using sentence-transformers"
dependencies = [
    "rag-core",
    "sentence-transformers>=2.7.0",
    "torch>=2.2.0",
    "numpy" # 벡터는 numpy 배열로 다뤄집니다.
]
[tool.uv.sources]
rag-core = { workspace = true }

[build-system]
requires = ["uv>=0.2.0"]
build-backend = "uv.backend"
EOF

# 임베더 클래스 코드 작성
mkdir -p packages/rag-embedder/rag_embedder
cat > packages/rag-embedder/rag_embedder/embedder.py << 'EOF'
import numpy as np
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
from rag_core.models import Chunk

class SentenceTransformerEmbedder:
    """텍스트를 벡터로 변환하는 책임을 지는 클래스"""
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("Embedding model loaded.")

    def embed_chunks(self, chunks: List[Chunk]) -> Tuple[List[Chunk], np.ndarray]:
        """청크 리스트를 임베딩하여 원본 청크와 벡터 배열을 반환합니다."""
        if not chunks:
            return [], np.array([])
        
        texts = [chunk.text for chunk in chunks]
        print(f"Embedding {len(texts)} chunks...")
        vectors = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        print("Embedding complete.")
        return chunks, vectors
    
    def embed_query(self, query: str) -> np.ndarray:
        """단일 쿼리 문자열을 임베딩합니다."""
        return self.model.encode(query, convert_to_numpy=True)
EOF
```

#### **2. `rag-engine` 패키지 생성 (`vicinity` 벡터 스토어)**

```bash
# 'rag-engine' 패키지를 초기화합니다.
uv init packages/rag-engine --package --name rag-engine

# pyproject.toml 파일을 작성합니다.
cat > packages/rag-engine/pyproject.toml << 'EOF'
[project]
name = "rag-engine"
version = "0.1.0"
description = "Vector search engine using vicinity"
dependencies = [
    "rag-core",
    # vicinity와 함께 고성능 백엔드인 FAISS를 설치합니다.
    "vicinity[faiss]>=0.1.0",
    "numpy",
]
[tool.uv.sources]
rag-core = { workspace = true }

[build-system]
requires = ["uv>=0.2.0"]
build-backend = "uv.backend"
EOF

# 엔진 클래스 코드 작성
mkdir -p packages/rag-engine/rag_engine
cat > packages/rag-engine/rag_engine/engine.py << 'EOF'
import numpy as np
from typing import List
from vicinity import Vicinity, Backend, Metric
from rag_core.models import Chunk, RetrievedChunk

class VicinityEngine:
    """Vicinity를 사용하여 벡터를 저장하고 검색하는 책임을 지는 클래스"""
    def __init__(self):
        self.vicinity_instance: Vicinity | None = None

    def build_index(self, chunks: List[Chunk], vectors: np.ndarray):
        """계산된 벡터로 vicinity 인덱스를 구축합니다."""
        if vectors.size == 0:
            print("No vectors to index.")
            return

        print(f"Building index with {len(chunks)} chunks using FAISS backend...")
        # from_vectors_and_items는 벡터와 해당 벡터의 원본 아이템을 받아 인덱스를 생성합니다.
        self.vicinity_instance = Vicinity.from_vectors_and_items(
            vectors=vectors.astype(np.float32), # FAISS는 float32를 요구합니다.
            items=chunks,
            backend_type=Backend.FAISS,
            metric=Metric.COSINE
        )
        print("Index build complete.")

    def search(self, query_vector: np.ndarray, top_k: int) -> List[RetrievedChunk]:
        """쿼리 벡터로 가장 유사한 청크를 검색합니다."""
        if self.vicinity_instance is None:
            return []

        # query()는 (item, score) 튜플의 리스트를 반환합니다.
        # item은 build_index 시점에 전달했던 원본 Chunk 객체입니다.
        results = self.vicinity_instance.query(query_vector.astype(np.float32), k=top_k)

        return [
            RetrievedChunk(**chunk.model_dump(), score=score)
            for chunk, score in results
        ]
EOF
```

-----

### **5.5. 미션 4: `rag-service` 및 `rag-api`로 파이프라인 완성**

**목표**: 분리된 모든 모듈을 조립(Orchestration)하여 하나의 완전한 서비스 흐름을 만들고, FastAPI를 통해 외부 사용자와 상호작용하는 최종 애플리케이션을 완성합니다.

#### **1. `rag-service` 패키지 생성 (파이프라인 오케스트레이션)**

```bash
uv init packages/rag-service --package --name rag-service
cat > packages/rag-service/pyproject.toml << 'EOF'
[project]
name = "rag-service"
version = "0.1.0"
description = "Orchestrates the entire RAG pipeline"
dependencies = [
    "rag-core", "storm-client", "rag-embedder", "rag-engine"
]
[tool.uv.sources]
rag-core = { workspace = true }
storm-client = { workspace = true }
rag-embedder = { workspace = true }
rag-engine = { workspace = true }

[build-system]
requires = ["uv>=0.2.0"]
build-backend = "uv.backend"
EOF

mkdir -p packages/rag-service/rag_service
cat > packages/rag-service/rag_service/service.py << 'EOF'
import asyncio
import uuid
from typing import List
from rag_core.models import Chunk, QueryRequest, FinalAnswer, ParsedPage
from storm_client.client import StormApiClient
from rag_embedder.embedder import SentenceTransformerEmbedder
from rag_engine.engine import VicinityEngine

class RAGService:
    """모든 모듈을 조립하여 RAG 파이프라인을 실행하는 서비스"""
    def __init__(self, client: StormApiClient, embedder: SentenceTransformerEmbedder, engine: VicinityEngine):
        self.client = client
        self.embedder = embedder
        self.engine = engine
        self.jobs = {}  # 인메모리 작업 상태 추적용

    def _chunk_pages(self, pages: List[ParsedPage], document_id: str, chunk_size=1000, overlap=100) -> List[Chunk]:
        """파싱된 페이지를 텍스트 청크로 분할합니다."""
        all_chunks = []
        for page in pages:
            content = page.content
            for i in range(0, len(content), chunk_size - overlap):
                all_chunks.append(Chunk(
                    id=str(uuid.uuid4()),
                    document_id=document_id,
                    text=content[i:i + chunk_size],
                    page_number=page.pageNumber
                ))
        return all_chunks

    async def process_document_in_background(self, job_id: str, document_id: str):
        """백그라운드에서 실행될 작업 폴링, 청킹, 임베딩, 인덱싱 파이프라인"""
        print(f"Starting background processing for job: {job_id}")
        while True:
            try:
                job, pages = await self.client.get_job_result(job_id)
                self.jobs[job_id] = job.state
                print(f"Polling job {job_id}, current state: {job.state}")

                if job.state == "COMPLETED":
                    # 1. Chunking
                    chunks = self._chunk_pages(pages, document_id)
                    # 2. Embedding
                    chunks, vectors = self.embedder.embed_chunks(chunks)
                    # 3. Indexing
                    self.engine.build_index(chunks, vectors)
                    print(f"Job {job_id} completed successfully.")
                    break
                elif job.state in ["FAILED", "ERROR"]:
                    print(f"Job {job_id} failed.")
                    break
                
                await asyncio.sleep(5)  # 5초 간격으로 폴링
            except Exception as e:
                print(f"Error processing job {job_id}: {e}")
                self.jobs[job_id] = "ERROR"
                break
    
    async def answer_query(self, query: QueryRequest) -> FinalAnswer:
        """사용자 질문에 대해 답변을 생성합니다."""
        # 1. 쿼리 임베딩
        query_vector = self.embedder.embed_query(query.query)
        
        # 2. 유사도 검색
        retrieved_context = self.engine.search(query_vector, query.top_k)
        
        # 3. 답변 생성 (간단한 조합)
        context_str = "\n\n---\n\n".join([c.text for c in retrieved_context])
        generated_answer = f"Based on the retrieved context, here is the relevant information for '{query.query}':\n\n{context_str}"

        return FinalAnswer(
            query=query.query, 
            generated_answer=generated_answer, 
            retrieved_context=retrieved_context
        )
EOF
```

#### **2. `rag-api` 패키지 생성 (최종 인터페이스)**

```bash
uv init packages/rag-api --package --name rag-api
cat > packages/rag-api/pyproject.toml << 'EOF'
[project]
name = "rag-api"
version = "0.1.0"
description = "FastAPI interface for the RAG pipeline"
dependencies = [
    "rag-core", "rag-service",
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.20.0",
    "python-multipart"
]
[tool.uv.sources]
rag-core = { workspace = true }
rag-service = { workspace = true }

[build-system]
requires = ["uv>=0.2.0"]
build-backend = "uv.backend"
EOF

mkdir -p packages/rag-api/rag_api
cat > packages/rag-api/rag_api/main.py << 'EOF'
import os
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from rag_core.models import QueryRequest, FinalAnswer, Job
from rag_service.service import RAGService
from storm_client.client import StormApiClient
from rag_embedder.embedder import SentenceTransformerEmbedder
from rag_engine.engine import VicinityEngine

# --- 환경 변수에서 설정 로드 ---
STORM_API_URL = os.getenv("STORM_API_URL", "https://live-storm-apis-parse-router.sionic.im")
STORM_API_TOKEN = os.getenv("STORM_API_TOKEN") # 실제 운영 시에는 반드시 토큰 설정 필요
UPLOAD_DIR = "/tmp/vicinity_rag_uploads"

if not STORM_API_TOKEN:
    print("Warning: STORM_API_TOKEN environment variable not set. Using a demo token.")
    STORM_API_TOKEN = "demo_Kx8fH9mN2pQrS3vT5wY7zA"

# --- 의존성 주입 (DI): 애플리케이션 시작 시 모든 컴포넌트를 한 번만 생성 ---
os.makedirs(UPLOAD_DIR, exist_ok=True)

client = StormApiClient(base_url=STORM_API_URL, token=STORM_API_TOKEN)
embedder = SentenceTransformerEmbedder()
engine = VicinityEngine()
rag_service = RAGService(client=client, embedder=embedder, engine=engine)
# ---

app = FastAPI(
    title="Vicinity-based RAG API",
    description="A modular RAG pipeline using Storm API, Sentence Transformers, and Vicinity."
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
        background_tasks.add_task(rag_service.process_document_in_background, job.job_id, job.job_id)
        
        return job
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start ingestion job: {e}")

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
    return {"status": "ok", "engine_indexed": rag_service.engine.vicinity_instance is not None}
EOF
```

-----

### **5.6. 전체 프로젝트 실행 및 검증**

**목표**: `uv` 명령어를 사용하여 전체 워크스페이스의 의존성을 동기화하고, 최종 애플리케이션을 실행하여 모든 파이프라인이 정상적으로 동작하는지 검증합니다.

```bash
# 1. 의존성 동기화
# 모든 'packages/' 내 pyproject.toml을 읽어 하나의 uv.lock 파일을 생성하고,
# .venv 가상 환경에 모든 의존성(httpx, pypdf, sentence-transformers, vicinity 등)을 설치합니다.
# 이 과정에서 uv의 빠른 속도와 효율적인 캐싱을 경험할 수 있습니다.
echo "Syncing all workspace dependencies..."
uv sync

# 2. API 서버 실행
# --package 플래그를 사용하여 rag-api 모듈의 컨텍스트에서 uvicorn 서버를 실행합니다.
# 워크스페이스 덕분에 다른 모듈의 코드를 자동으로 인식합니다.
echo "Starting the RAG API server..."
uv run --package rag-api uvicorn rag_api.main:app --reload

# 3. API 테스트 (새 터미널에서 실행)
# (테스트할 PDF 파일 'my_document.pdf'를 현재 디렉터리에 준비했다고 가정합니다.)
echo "Running API tests..."

# ① PDF 파일 업로드 (job_id가 반환됨)
echo "Uploading document..."
JOB_ID=$(curl -s -X POST "http://localhost:8000/ingest" -F "file=@my_document.pdf" | python -c "import sys, json; print(json.load(sys.stdin)['job_id'])")
echo "Ingestion started with Job ID: $JOB_ID"

# ② 작업 상태 확인 (COMPLETED가 될 때까지 몇 초 간격으로 확인)
echo "Polling for job completion..."
while true; do
  STATUS=$(curl -s "http://localhost:8000/ingest/status/$JOB_ID" | python -c "import sys, json; print(json.load(sys.stdin)['state'])")
  echo "Current status: $STATUS"
  if [ "$STATUS" = "COMPLETED" ]; then
    break
  fi
  sleep 5
done

# ③ (작업 완료 후) 질문하기
echo "Querying the RAG system..."
curl -X POST "http://localhost:8000/query" \
-H "Content-Type: application/json" \
-d '{
  "query": "What is the main idea of this document?",
  "top_k": 2
}' | python -m json.tool
```
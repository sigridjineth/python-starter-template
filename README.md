# MISSION 5: Vicinity 기반 RAG 파이프라인 구축

## 목표

[`vicinity`](https://github.com/MinishLab/vicinity)를 벡터 검색 엔진으로 사용하고, [`STORM Parse`](https://stormparse.sionic.ai/)를 문서 파싱 엔진으로 사용합니다.

각 모듈의 책임을 명확하게 분리하는 RAG 파이프라인을 구축한다. 텍스트를 벡터로 변환하는 '임베딩'과 벡터를 저장하고 검색하는 '인덱싱/서빙'의 책임을 완전히 분리하여 실제 현업 수준의 아키텍처 설계 원칙을 체득한다.

## 산출물

- 동작하는 uv Workspace (루트 pyproject.toml + packages/*)
- `rag-core` 패키지: Pydantic 기반 데이터 모델 (Job, Chunk, QueryRequest 등)
- `storm-client` 패키지: Storm Parse API와의 HTTP 통신 전담
- `rag-embedder` 패키지: sentence-transformers를 사용한 텍스트 임베딩 전담
- `rag-engine` 패키지: vicinity를 사용한 벡터 저장/검색 전담
- `rag-service` 패키지: 전체 파이프라인 오케스트레이션
- `rag-api` 패키지: FastAPI 기반 REST API 인터페이스
- 테스트 코드: 각 모듈의 기능을 검증하는 단위 테스트
- 문서: 본 README.md

## 전제 조건

- Python 3.11 이상
- uv 설치 및 사용 (pip 사용 금지)
- Storm Parse API 토큰 (선택사항, 미설정시 데모 토큰 사용)

## Workspace 구성 요구사항

### 루트 pyproject.toml
- `[tool.uv.workspace]`로 멤버 선언: `members = ["packages/*"]`
- 개발 의존성 포함: pytest, mypy 등

### 패키지 구조
```
packages/
├── rag-core/       # name = "rag-core", build-backend = "uv.backend"
├── storm-client/   # name = "storm-client", dependencies = ["rag-core", "httpx"]
├── rag-embedder/   # name = "rag-embedder", dependencies = ["rag-core", "sentence-transformers"]
├── rag-engine/     # name = "rag-engine", dependencies = ["rag-core", "vicinity[faiss]"]
├── rag-service/    # name = "rag-service", dependencies = ["rag-core", "storm-client", "rag-embedder", "rag-engine"]
└── rag-api/        # name = "rag-api", dependencies = ["rag-core", "rag-service", "fastapi", "uvicorn"]
```

## 기능 요구사항

### rag-core (데이터 모델)
- `Job`: Storm API 작업 상태 (job_id: str, state: str)
- `ParsedPage`: 파싱된 페이지 데이터 (pageNumber: int, content: str)
- `Chunk`: 텍스트 청크 (id: str, document_id: str, text: str, page_number: int)
- `QueryRequest`: 검색 요청 (query: str, top_k: int = 3)
- `RetrievedChunk`: 검색 결과 (Chunk + score: float)
- `FinalAnswer`: 최종 응답 (query: str, generated_answer: str, retrieved_context: List[RetrievedChunk])

### storm-client (외부 API 통신)
- `StormApiClient` 클래스:
  - `upload_document(file_path: str) -> Job`: PDF 업로드
  - `get_job_result(job_id: str) -> tuple[Job, Optional[List[ParsedPage]]]`: 작업 결과 조회
- httpx를 사용한 비동기 HTTP 통신
- Bearer 토큰 인증 지원

### rag-embedder (텍스트 임베딩)
- `SentenceTransformerEmbedder` 클래스:
  - `embed_chunks(chunks: List[Chunk]) -> Tuple[List[Chunk], np.ndarray]`: 청크 리스트 임베딩
  - `embed_query(query: str) -> np.ndarray`: 쿼리 임베딩
- 모델: "all-MiniLM-L6-v2" (기본값)
- 벡터 출력: numpy 배열

### rag-engine (벡터 검색)
- `VicinityEngine` 클래스:
  - `build_index(chunks: List[Chunk], vectors: np.ndarray)`: 인덱스 구축
  - `search(query_vector: np.ndarray, top_k: int) -> List[RetrievedChunk]`: 유사도 검색
- Backend: FAISS
- Metric: COSINE
- vicinity의 `from_vectors_and_items` API 사용

### rag-service (파이프라인 오케스트레이션)
- `RAGService` 클래스:
  - 의존성: StormApiClient, SentenceTransformerEmbedder, VicinityEngine
  - `process_document_in_background(job_id: str, document_id: str)`: 비동기 문서 처리
  - `answer_query(query: QueryRequest) -> FinalAnswer`: 질의 응답
- 청킹 로직: chunk_size=1000, overlap=100
- 작업 상태 추적 (인메모리)

### rag-api (REST API)
- FastAPI 애플리케이션:
  - `POST /ingest`: PDF 업로드 (BackgroundTasks로 비동기 처리, 202 반환)
  - `GET /ingest/status/{job_id}`: 작업 상태 확인
  - `POST /query`: 질의 응답
  - `GET /`: 헬스 체크
- 의존성 주입: 애플리케이션 시작시 모든 컴포넌트 생성
- 업로드 디렉토리: `/tmp/vicinity_rag_uploads`

## 개발 프로세스 (필수)

### TDD 사이클 준수
1. Red: 실패하는 테스트 작성
2. Green: 테스트를 통과하는 최소한의 코드 작성
3. Refactor: 코드 품질 개선 (테스트 통과 유지)

### 구조적 변경과 행위 변경 분리
- 구조적 변경: 패키지 생성, 빌드 시스템 변경, 의존성 추가
- 행위 변경: 기능 구현, 버그 수정, 로직 변경
- 각각을 별도 커밋으로 분리

## 테스트 요구사항

### 단위 테스트 (각 패키지별)
- rag-core: 모델 직렬화, 필드 검증
- storm-client: API 호출 모킹 (pytest-httpx)
- rag-embedder: 벡터 차원 검증
- rag-engine: 인덱싱/검색 동작 검증
- rag-service: 파이프라인 통합 검증

### 통합 테스트
- API 엔드포인트 테스트 (httpx.AsyncClient)
- 전체 파이프라인 동작 검증

## 품질/검증 기준 (Definition of Done)

- `make test` → 모든 테스트 통과
- `make format` → 코드 포맷 정리됨
- `make check` → ruff, mypy, pyrefly 모두 통과
- 모든 패키지가 `uv.backend` 사용
- 불필요한 의존성 없음
- 명확한 책임 분리

## 실행/개발 명령어

```bash
# 워크스페이스 동기화
uv sync

# 테스트 실행
make test

# API 서버 실행
make run
# 또는
uv run --package rag-api uvicorn rag_api.main:app --reload

# 코드 품질 검사
make check

# 코드 포맷팅
make format
```

## 디렉토리 구조

```
.
├── pyproject.toml            # Workspace 루트 설정
├── uv.lock                   # 의존성 잠금 파일
├── Makefile                  # 개발 명령어
├── packages/
│   ├── rag-core/
│   │   ├── pyproject.toml    # uv.backend 사용
│   │   └── src/rag_core/
│   │       └── models.py
│   ├── storm-client/
│   │   ├── pyproject.toml
│   │   └── src/storm_client/
│   │       └── client.py
│   ├── rag-embedder/
│   │   ├── pyproject.toml
│   │   └── src/rag_embedder/
│   │       └── embedder.py
│   ├── rag-engine/
│   │   ├── pyproject.toml
│   │   └── src/rag_engine/
│   │       └── engine.py
│   ├── rag-service/
│   │   ├── pyproject.toml
│   │   └── src/rag_service/
│   │       └── service.py
│   └── rag-api/
│       ├── pyproject.toml
│       └── src/rag_api/
│           └── main.py
└── docs/
    ├── CURRICULUM.md         # 교육과정
    └── plan.md               # 테스트 계획

```

## 제약/금지사항

- pip 사용 금지 (항상 uv add, uv sync, uv run 사용)
- requirements.txt 직접 수정 금지
- hatchling 사용 금지 (uv.backend 사용)
- txtai 사용 금지 (vicinity 사용)
- DB/영속화 금지 (인메모리만 사용)
- 모든 패키지는 src/ 레이아웃 사용

## 평가 기준

1. **아키텍처 설계** (40%)
   - 책임 분리 원칙 준수
   - 의존성 방향 적절성
   - 모듈 간 결합도/응집도

2. **코드 품질** (30%)
   - TDD 사이클 준수
   - 명명 규칙 및 가독성
   - 에러 처리 적절성

3. **기능 완성도** (20%)
   - 모든 API 엔드포인트 동작
   - 테스트 커버리지
   - 엣지 케이스 처리

4. **개발 프로세스** (10%)
   - 커밋 히스토리 품질
   - 구조/행위 변경 분리
   - 문서화 수준

## 환경 변수

```bash
# Storm API 설정 (선택사항)
STORM_API_URL=https://live-storm-apis-parse-router.sionic.im
STORM_API_TOKEN=your-token-here  # 미설정시 데모 토큰 사용
```

## API 사용 예시

```bash
# 1. PDF 업로드
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@sample.pdf"
# 응답: {"job_id": "...", "state": "PROCESSING"}

# 2. 상태 확인
curl "http://localhost:8000/ingest/status/{job_id}"
# 응답: {"job_id": "...", "state": "COMPLETED"}

# 3. 질의
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "문서의 주요 내용은?", "top_k": 3}'
# 응답: {"query": "...", "generated_answer": "...", "retrieved_context": [...]}
```

## 트러블슈팅

### pyrefly 오류
- `project-excludes`에 `packages/**/*` 추가
- 워크스페이스 패키지는 이미 개별적으로 검사됨

### vicinity 설치 오류
- FAISS 백엔드 필요: `vicinity[faiss]`
- numpy 버전 호환성 확인

### 임베딩 모델 다운로드
- 첫 실행시 sentence-transformers 모델 자동 다운로드
- 오프라인 환경에서는 사전 다운로드 필요
# Python uv 기반 멀티모듈(Workspace) 개발 실습 교육과정

## 목차
1. [기초 개념](#1-기초-개념)
2. [환경 설정](#2-환경-설정)
3. [첫 번째 Workspace 프로젝트](#3-첫-번째-workspace-프로젝트)
4. [멀티모듈 구조 설계](#4-멀티모듈-구조-설계)
5. [실전 프로젝트: FastAPI 멀티모듈 애플리케이션](#5-실전-프로젝트-fastapi-멀티모듈-애플리케이션)
6. [의존성 관리 심화](#6-의존성-관리-심화)
7. [개발 워크플로우](#7-개발-워크플로우)
8. [테스트 전략](#8-테스트-전략)
9. [CI/CD 통합](#9-cicd-통합)
10. [고급 주제](#10-고급-주제)

---

## 1. 기초 개념

### 1.1 Monorepo와 멀티모듈의 이해

**Monorepo**는 여러 프로젝트를 하나의 Git 저장소에서 관리하는 방식입니다.

**장점:**
- 코드 공유가 쉬움
- 원자적 커밋으로 여러 프로젝트 동시 변경
- 일관된 도구 사용
- 단일 이슈 트래커

**단점:**
- 저장소 크기 증가
- 빌드 시간 증가 가능성
- 권한 관리의 복잡성

### 1.2 uv란?

**uv**는 Rust로 작성된 초고속 Python 패키지 매니저로, pip와 pip-tools를 대체합니다.

**주요 특징:**
- **속도**: pip보다 10-100배 빠름
- **Workspace 지원**: 멀티모듈 프로젝트를 위한 내장 지원
- **단일 lockfile**: 전체 workspace에 대한 일관된 의존성
- **교차 플랫폼**: Windows, macOS, Linux 지원

### 1.3 Workspace 개념

**Workspace**는 공통 의존성을 공유하는 여러 Python 패키지의 모음입니다.

```
my-project/
├── pyproject.toml          # Workspace 루트 설정
├── uv.lock                 # 공유 lockfile
├── packages/
│   ├── core/
│   │   └── pyproject.toml  # 개별 패키지 설정
│   └── api/
│       └── pyproject.toml  # 개별 패키지 설정
```

---

## 2. 환경 설정

### 2.1 uv 설치

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 설치 확인
uv --version
```

### 2.2 개발 도구 설정

```bash
# 프로젝트 디렉토리 생성
mkdir learn-uv-workspace
cd learn-uv-workspace

# Git 초기화
git init

# .gitignore 생성
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/

# uv
.venv/
uv.lock

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/

# Distribution
dist/
build/
*.egg-info/
EOF
```

---

## 3. 첫 번째 Workspace 프로젝트

### 3.1 Workspace 루트 생성

```bash
# Workspace 루트 초기화
uv init --package

# 루트 pyproject.toml 수정
cat > pyproject.toml << 'EOF'
[project]
name = "my-workspace"
version = "0.1.0"
description = "Learning uv workspace"
readme = "README.md"
requires-python = ">=3.11"
dependencies = []

[tool.uv.workspace]
members = ["packages/*"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
EOF
```

### 3.2 첫 번째 패키지 생성

```bash
# 패키지 디렉토리 생성
mkdir -p packages

# core 패키지 생성
uv init packages/core --package --name my-core

# core 패키지 설정
cat > packages/core/pyproject.toml << 'EOF'
[project]
name = "my-core"
version = "0.1.0"
description = "Core utilities"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["my_core"]
EOF
```

### 3.3 코드 작성

```bash
# core 패키지 구조 생성
mkdir -p packages/core/my_core
touch packages/core/my_core/__init__.py

# 간단한 모델 생성
cat > packages/core/my_core/models.py << 'EOF'
from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime = datetime.now()
    
    def greeting(self) -> str:
        return f"Hello, {self.name}!"
EOF
```

### 3.4 의존성 설치 및 테스트

```bash
# 전체 workspace 의존성 설치
uv sync

# Python 쉘에서 테스트
uv run python << 'EOF'
from my_core.models import User
user = User(id=1, name="Alice", email="alice@example.com")
print(user.greeting())
print(user.model_dump_json())
EOF
```

---

## 4. 멀티모듈 구조 설계

### 4.1 두 번째 패키지 추가

```bash
# api 패키지 생성
uv init packages/api --package --name my-api

# api 패키지가 core에 의존하도록 설정
cat > packages/api/pyproject.toml << 'EOF'
[project]
name = "my-api"
version = "0.1.0"
description = "API layer"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "my-core",
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.20.0",
]

[tool.uv.sources]
my-core = { workspace = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["my_api"]
EOF
```

### 4.2 API 코드 작성

```bash
# API 패키지 구조 생성
mkdir -p packages/api/my_api
touch packages/api/my_api/__init__.py

# FastAPI 앱 생성
cat > packages/api/my_api/main.py << 'EOF'
from fastapi import FastAPI
from my_core.models import User
from typing import List

app = FastAPI(title="My API")

# 메모리 저장소
users: List[User] = []

@app.get("/")
def read_root():
    return {"message": "Welcome to My API"}

@app.post("/users/", response_model=User)
def create_user(user: User):
    users.append(user)
    return user

@app.get("/users/", response_model=List[User])
def list_users():
    return users

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    for user in users:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")
EOF
```

### 4.3 의존성 동기화 및 실행

```bash
# 전체 workspace 동기화
uv sync

# API 서버 실행
uv run --package my-api uvicorn my_api.main:app --reload
```

---

## 5. 실전 프로젝트: FastAPI 멀티모듈 애플리케이션

```

#### **2. `rag-api` 기능 명세 및 구현 계획**

  * **기능 명세**: FastAPI를 사용하여 비동기 문서 처리 요청을 받고, 작업 상태를 조회하며, 질의응답 기능을 제공하는 엔드포인트를 구현합니다.
  * **구현 계획**:
    1.  `/ingest` 엔드포인트는 `UploadFile`을 받아 `RAGService`에 처리를 위임하고, 즉시 `job_id`를 반환합니다. FastAPI의 `BackgroundTasks`를 사용하여 폴링 및 인덱싱 작업을 백그라운드에서 실행합니다.
    2.  `/ingest/status/{job_id}` 엔드포인트를 추가하여 작업의 현재 상태를 조회할 수 있게 합니다.
    3.  `/query` 엔드포인트는 사용자 질문을 받아 처리하고 답변을 반환합니다.

<!-- end list -->

```bash
# ... 패키지 생성 및 pyproject.toml 설정 ...
# packages/rag-api/rag_api/main.py 작성
cat > packages/rag-api/rag_api/main.py << 'EOF'
import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from rag_core.models import QueryRequest, FinalAnswer, Job
from rag_service.service import RAGService
from storm_client.client import StormApiClient
from rag_engine.engine import TxtaiEngine

# --- DI 및 설정 ---
STORM_API_URL = os.getenv("STORM_API_URL", "https://live-storm-apis-parse-router.sionic.im")
STORM_API_TOKEN = os.getenv("STORM_API_TOKEN", "demo_Kx8fH9mN2pQrS3vT5wY7zA")
UPLOAD_DIR = "/tmp/api_rag_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

client = StormApiClient(base_url=STORM_API_URL, token=STORM_API_TOKEN)
engine = TxtaiEngine()
rag_service = RAGService(client=client, engine=engine)
# ---

app = FastAPI(title="API-Driven RAG Pipeline")

@app.post("/ingest", response_model=Job)
async def ingest_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Uploads a PDF, starts async processing, and returns a job ID immediately."""
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    document_id = str(uuid.uuid4())
    job = await rag_service.client.upload_document(file_path)
    rag_service.jobs[job.job_id] = job.state
    
    # 백그라운드에서 폴링 및 인덱싱 작업 시작
    background_tasks.add_task(rag_service.process_document_in_background, job.job_id, document_id)
    
    return job

@app.get("/ingest/status/{job_id}", response_model=Job)
async def get_job_status(job_id: str):
    """Checks the status of an ingestion job."""
    state = rag_service.jobs.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")
    return Job(job_id=job_id, state=state)

@app.post("/query", response_model=FinalAnswer)
async def ask_question(query: QueryRequest):
    return await rag_service.answer_query(query)
EOF
```

-----

### **5.5. 전체 프로젝트 실행 및 검증**

```bash
# 1. 의존성 동기화
uv sync

# 2. API 서버 실행
uv run --package rag-api uvicorn rag_api.main:app --reload

# 3. API 테스트 (터미널)
# ① PDF 파일 업로드 (job_id가 반환됨)
# curl -X POST "http://localhost:8000/ingest" -F "file=@/path/to/your/document.pdf"

# ② 작업 상태 확인 (반환된 job_id 사용)
# curl "http://localhost:8000/ingest/status/{your_job_id}"

# ③ (작업 완료 후) 질문하기
# curl -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{"query": "..."}'
```

---

## 6. 의존성 관리 심화

### 6.1 공통 의존성 관리

```toml
# 루트 pyproject.toml에서 공통 의존성 정의
[project]
dependencies = [
    # 모든 패키지가 사용하는 공통 의존성
    "pydantic>=2.0.0",
    "structlog>=24.0.0",
]

[tool.uv.sources]
# 버전 제약 통합 관리
pydantic = ">=2.0.0,<3.0.0"
```

### 6.2 개발 의존성 관리

```toml
# 루트에 개발 의존성 추가
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
    "black>=23.0.0",
]

# 개발 의존성 설치
uv sync --extra dev
```

### 6.3 버전 충돌 해결

```bash
# 의존성 트리 확인
uv tree

# 특정 패키지의 의존성 확인
uv tree --package ecommerce-api

# 의존성 업데이트
uv lock --upgrade-package pydantic
```

---

## 7. 개발 워크플로우

### 7.1 Makefile 설정

```makefile
# Makefile
.PHONY: help init format lint type-check test clean

help:
	@echo "Available commands:"
	@echo "  make init        - Initialize development environment"
	@echo "  make format      - Format code with black"
	@echo "  make lint        - Run linting with ruff"
	@echo "  make type-check  - Run type checking with mypy"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Clean up cache files"

init:
	uv sync --extra dev
	pre-commit install

format:
	uv run black packages/
	uv run ruff check --fix packages/

lint:
	uv run ruff check packages/

type-check:
	uv run mypy packages/

test:
	uv run pytest packages/ -v --cov=packages --cov-report=html

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov
```

### 7.2 Pre-commit 설정

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

---

## 8. 테스트 전략

### 8.1 단위 테스트

```python
# packages/services/tests/test_product_service.py
import pytest
from unittest.mock import AsyncMock
from ecommerce_core.models.product import Product
from ecommerce_core.exceptions.base import NotFoundError, ValidationError
from ecommerce_services.product_service import ProductService

@pytest.fixture
def mock_repository():
    return AsyncMock()

@pytest.fixture
def product_service(mock_repository):
    return ProductService(mock_repository)

@pytest.mark.asyncio
async def test_create_product_success(product_service, mock_repository):
    # Given
    product = Product(name="Test Product", price="10.00", stock=5)
    mock_repository.create.return_value = Product(
        id=1, name="Test Product", price="10.00", stock=5
    )
    
    # When
    result = await product_service.create_product(product)
    
    # Then
    assert result.id == 1
    assert result.name == "Test Product"
    mock_repository.create.assert_called_once_with(product)

@pytest.mark.asyncio
async def test_create_product_invalid_price(product_service):
    # Given
    product = Product(name="Test Product", price="-10.00", stock=5)
    
    # When/Then
    with pytest.raises(ValidationError):
        await product_service.create_product(product)
```

### 8.2 통합 테스트

```python
# packages/api/tests/test_integration.py
import pytest
from httpx import AsyncClient
from ecommerce_api.main import create_app

@pytest.fixture
async def client():
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_product_lifecycle(client):
    # Create product
    response = await client.post("/products/", json={
        "name": "Test Product",
        "price": "99.99",
        "stock": 10
    })
    assert response.status_code == 200
    product = response.json()
    assert product["id"] == 1
    
    # Get product
    response = await client.get(f"/products/{product['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Product"
    
    # Update stock
    response = await client.patch(
        f"/products/{product['id']}/stock?quantity=5"
    )
    assert response.status_code == 200
    assert response.json()["new_stock"] == 15
```

---

## 9. CI/CD 통합

### 9.1 GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Install uv
      uses: astral-sh/setup-uv@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      run: uv python install ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: uv sync --extra dev
    
    - name: Lint with ruff
      run: uv run ruff check .
    
    - name: Type check with mypy
      run: uv run mypy packages/
    
    - name: Test with pytest
      run: uv run pytest packages/ --cov=packages --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### 9.2 Docker 배포

```dockerfile
# Dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy workspace files
COPY pyproject.toml uv.lock ./
COPY packages/ packages/

# Install dependencies
RUN uv sync --frozen --no-dev

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --from=builder /app/packages /app/packages

# Set Python path
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Run the application
CMD ["uvicorn", "ecommerce_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 10. 고급 주제

### 10.1 동적 버전 관리

```python
# packages/core/ecommerce_core/__version__.py
import importlib.metadata

try:
    __version__ = importlib.metadata.version("ecommerce-core")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0+unknown"
```

### 10.2 플러그인 시스템

```python
# packages/core/ecommerce_core/plugins.py
from abc import ABC, abstractmethod
from typing import Dict, Type

class Plugin(ABC):
    @abstractmethod
    def initialize(self):
        pass

class PluginRegistry:
    _plugins: Dict[str, Type[Plugin]] = {}
    
    @classmethod
    def register(cls, name: str, plugin: Type[Plugin]):
        cls._plugins[name] = plugin
    
    @classmethod
    def get(cls, name: str) -> Type[Plugin]:
        return cls._plugins.get(name)
```

### 10.3 성능 최적화

```toml
# 컴파일 최적화
[tool.uv]
compile-bytecode = true

# 병렬 설치
[tool.uv.pip]
concurrent-builds = 4
```

### 10.4 보안 스캔

```bash
# 의존성 보안 스캔
uv run pip-audit

# SAST 스캔
uv run bandit -r packages/
```

---

## 실습 과제

### 과제 1: 기본 Workspace 생성
1. 3개의 패키지를 가진 workspace 생성
2. 패키지 간 의존성 설정
3. 각 패키지에 간단한 기능 구현

### 과제 2: FastAPI 멀티모듈 애플리케이션
1. 위 예제를 확장하여 주문(Order) 기능 추가
2. 새로운 `orders` 패키지 생성
3. 주문 서비스와 API 엔드포인트 구현

### 과제 3: 테스트 및 CI/CD
1. 모든 패키지에 대한 단위 테스트 작성
2. 통합 테스트 구현
3. GitHub Actions CI 파이프라인 설정

### 과제 4: 프로덕션 배포
1. Docker 이미지 빌드
2. docker-compose로 로컬 환경 구성
3. Kubernetes 배포 매니페스트 작성

---

## 추가 리소스

- [uv 공식 문서](https://docs.astral.sh/uv/)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Monorepo 베스트 프랙티스](https://monorepo.tools/)

---

## 마무리

이 교육과정을 통해 Python uv workspace를 활용한 멀티모듈 개발의 핵심 개념과 실제 적용 방법을 학습했습니다. 실제 프로젝트에서는 각 팀의 요구사항에 맞게 구조를 조정하고, 지속적으로 개선해 나가는 것이 중요합니다.
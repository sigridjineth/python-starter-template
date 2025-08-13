## MISSION 1: 첫 번째 Workspace 프로젝트 + 멀티모듈 구조 설계 요구사항
**목표**
- uv 기반 Python Workspace를 구성하고, 멀티모듈(패키지) 구조로 `core`(도메인)와 `api`(애플리케이션 레이어)를 분리하여 구현한다.
- Kent Beck의 TDD와 Tidy First 원칙을 준수한다.

**산출물**
- 동작하는 uv Workspace(루트 `pyproject.toml` + `packages/*`).
- `my-core` 패키지: Pydantic 기반 도메인 모델(`User`).
- `my-api` 패키지: FastAPI 애플리케이션(`my_api.main:app`).
- 테스트 코드: 기능 요구사항을 검증하는 단위/통합 테스트(`uv run pytest` 전체 통과).
- 문서: 본 README와 `docs/plan.md`의 테스트 계획.

**전제 조건**
- Python 3.11 이상
- uv 설치 및 사용 (pip 금지)

**Workspace 구성 요구사항**
- 루트 `pyproject.toml`:
  - `[tool.uv.workspace]`로 멤버를 선언: `members = ["packages/*"]`
  - 로컬 패키지 소스 매핑: `[tool.uv.sources]`에 `my-core`, `my-api`를 `workspace = true`로 지정
  - 루트 `dependencies`에 `my-core`, `my-api`를 포함하여 워크스페이스 해석 가능하게 함
- 패키지 디렉터리:
  - `packages/core/pyproject.toml` → `project.name = "my-core"`, `build-system = hatchling`, `packages = ["my_core"]`
  - `packages/api/pyproject.toml` → `project.name = "my-api"`, `dependencies`에 `my-core`, `fastapi`, `uvicorn[standard]`
  - 각 패키지에 `README.md` 존재(빌드 무결성 보장)

**Core 패키지 기능 요구사항 (`my-core`)**
- 모듈: `my_core.models`
- 클래스: `User` (Pydantic BaseModel)
  - 필드: `id: int`, `name: str`, `email: str`, `created_at: datetime = datetime.now()`
  - 메서드: `greeting(self) -> str` → 정확히 `"Hello, {name}!"` 반환
  - 직렬화: `model_dump()`에 최소 `id`, `name`, `email` 키가 포함되어야 함
  - 제약: 외부 I/O나 DB 의존 금지, 순수 데이터 모델

**API 패키지 기능 요구사항 (`my-api`)**
- 애플리케이션 엔트리: `my_api.main:app` (FastAPI 인스턴스)
- 라우트:
  - `GET /` → `{ "message": "Welcome to My API" }`
  - 인메모리 저장소: `users: List[User] = []` (프로세스 생명주기 내 유지)
  - `POST /users/` → 요청 본문 `User`(JSON) 수신 후 동일한 유저 반환(에코), 상태코드 200
  - `GET /users/` → 현재 저장된 모든 유저 리스트 반환
  - `GET /users/{user_id}` → `id` 일치 시 해당 유저 반환, 없으면 `404` + `{"detail": "User not found"}`
- 스키마: Pydantic v2 기반 타입힌트 준수, `response_model` 지정으로 응답 스키마 일관성 유지
- 비범위 사항: 업데이트/삭제/영속화/인증/페이지네이션 등은 본 미션 범위 외

**개발 프로세스(필수)**
- TDD 사이클(Red → Green → Refactor)을 엄격히 적용
- 한 번에 하나의 테스트만 추가하고, 통과시키는 최소한의 코드만 작성
- 구조적 변경과 행위 변경을 분리(Tidy First):
  - 예: 워크스페이스/모듈 구조 추가(구조적) → 테스트 추가/통과(행위)
- 모든 테스트가 통과한 상태에서만 리팩터링 수행

**테스트 요구사항**
- Core(User):
  - `greeting()`이 정확히 `"Hello, {name}!"`를 반환한다
  - `User`는 `id`, `name`, `email`로 인스턴스화할 수 있다
  - `model_dump()` 결과에 `id`, `name`, `email` 키가 존재한다
- API:
  - `GET /`는 `{"message": "Welcome to My API"}`와 200을 반환한다
  - `POST /users/`는 요청 `User`를 저장 후 동일 데이터를 200으로 반환한다
  - `GET /users/`는 리스트를 반환하며, 이전에 생성한 유저가 포함된다
  - `GET /users/{id}`는 존재 시 200 + 해당 유저, 미존재 시 404 반환
- 전부 `uv run pytest` 기준으로 통과해야 한다

**품질/검증 기준(Definition of Done)**
- `make test` → 모든 테스트 통과
- `make format` → 코드 포맷 정리됨
- `make check` → ruff, ty, mypy, pyrefly 모두 통과
- 불필요한 의존성, 미사용 코드 없음
- 명확한 네이밍과 의도 표현, 중복 최소화

**실행/개발 명령어**
- 워크스페이스 동기화: `uv sync`
- 테스트 실행: `uv run pytest`
- 애플리케이션 실행(미션 API): `make run`
- 애그리게이터 앱 실행(선택): `uv run uvicorn src.app.main:app --reload`

**디렉터리 구조(요약)**
```
.
├── pyproject.toml            # uv workspace 루트 설정
├── packages/
│   ├── core/
│   │   ├── pyproject.toml
│   │   └── my_core/
│   │       ├── __init__.py
│   │       └── models.py     # User
│   └── api/
│       ├── pyproject.toml
│       └── my_api/
│           ├── __init__.py
│           └── main.py       # FastAPI app + users 라우트
└── src/app/main.py           # (선택) /api로 my_api 마운트
```

**제약/금지사항**
- pip 사용 금지(항상 `uv add`, `uv sync`, `uv run` 사용)
- `requirements.txt` 직접 수정 금지(Deprecated)
- DB/외부 서비스 통합 금지(인메모리만 사용)

**평가 기준(예시)**
- TDD/커밋 규율 준수 여부(작고 빈번하며, 구조/행위 분리)
- 요구사항 충족도(기능/비기능)
- 가독성/명명/의도 표현, 테스트 명확성
- 의존성/구성의 간결성 및 적절성

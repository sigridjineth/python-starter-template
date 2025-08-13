.PHONY: init format check requirements test run

init:
	export PATH="$$HOME/.local/bin:$$PATH"
	wget -qO- https://astral.sh/uv/install.sh | sh
	uv venv
	. .venv/bin/activate
	uv sync
	uvx pyrefly init
	uvx mypy --version

format:
	uvx ruff format src

check:
	uvx ruff check src --fix; \
	uvx ty check src; \
	uvx mypy src; \
	uvx pyrefly check

requirements:
	uv export -o requirements.txt --without-hashes --without dev
	uv export -o requirements-dev.txt --without-hashes

test:
	@echo "Running all tests..."
	@echo "===================="
	@echo ""
	@echo "📦 Testing rag-core..."
	-@cd packages/rag-core && uv sync --extra test >/dev/null 2>&1 && uv run pytest -v
	@echo ""
	@echo "📦 Testing storm-client..."
	-@cd packages/storm-client && uv sync --extra test >/dev/null 2>&1 && uv run pytest -v
	@echo ""
	@echo "📦 Testing rag-engine..."
	-@cd packages/rag-engine && uv sync --extra test >/dev/null 2>&1 && uv run pytest -v
	@echo ""
	@echo "📦 Testing rag-service..."
	-@cd packages/rag-service && uv sync --extra test >/dev/null 2>&1 && uv run pytest -v
	@echo ""
	@echo "📦 Testing rag-api..."
	-@cd packages/rag-api && uv sync --extra test >/dev/null 2>&1 && uv run pytest -v
	@echo ""
	@echo "📦 Testing integration..."
	-@uv run pytest tests/ -v

run:
	uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

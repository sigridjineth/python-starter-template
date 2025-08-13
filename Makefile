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
	uv run pytest tests/ -v

# Test all packages in workspace using the test runner
test-all:
	@uv run python test_runner.py

# Quick test summary
test-quick:
	@echo "Running quick test summary..."
	@echo "================================"
	@cd packages/rag-core && echo "rag-core:" && uv run pytest -q
	@cd packages/storm-client && echo "storm-client:" && uv sync --extra test >/dev/null 2>&1 && uv run pytest -q
	@cd packages/rag-engine && echo "rag-engine:" && uv run pytest -q
	@cd packages/rag-service && echo "rag-service:" && uv run pytest -q
	@cd packages/rag-api && echo "rag-api:" && uv run pytest -q

# Test individual packages
test-core:
	@cd packages/rag-core && uv run pytest -v

test-storm:
	@cd packages/storm-client && uv sync --extra test && uv run pytest -v

test-engine:
	@cd packages/rag-engine && uv run pytest -v

test-service:
	@cd packages/rag-service && uv run pytest -v

test-api:
	@cd packages/rag-api && uv run pytest -v

run:
	uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

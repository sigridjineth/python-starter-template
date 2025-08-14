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
	@echo "Formatting code..."
	@uvx ruff format src
	@for pkg in rag-core storm-client rag-engine rag-service rag-api; do \
		echo "Formatting $$pkg..."; \
		cd packages/$$pkg/src && uvx ruff format . && cd ../../..; \
	done

check:
	@echo "Running linters and type checkers..."
	@echo "Checking main src..."
	-@uvx ruff check src --fix
	-@uvx mypy src
	@echo "Checking packages..."
	@for pkg in rag-core storm-client rag-engine rag-service rag-api; do \
		echo "Checking $$pkg..."; \
		cd packages/$$pkg/src && uvx ruff check . --fix && cd ../../..; \
	done
	@echo "Running pyrefly..."
	-@uvx pyrefly check

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
	uv run --package rag-api uvicorn rag_api.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: install lint format typecheck test coverage check clean

install:
	uv sync --group dev

lint:
	uv run ruff check .

format:
	uv run ruff check . --fix && uv run ruff format .

typecheck:
	uv run mypy src/

test:
	uv run pytest

coverage-html:
	uv run pytest --cov-report=html
	@echo "Report: htmlcov/index.html"

check: format typecheck test

clean:
	rm -rf .venv dist .mypy_cache .ruff_cache .coverage htmlcov __pycache__

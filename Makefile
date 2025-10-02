.PHONY: run test install build clean

run:
	uv run python -m pre_commit_starter

test:
	uv run pytest tests/ -v

install:
	uv pip install -e ".[dev]"
	uv run pre-commit install
	@echo "✅ Package installed with development dependencies"

build:
	uv build

clean:
	rm -rf build/ dist/ *.egg-info .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.py[co]" -delete 2>/dev/null || true

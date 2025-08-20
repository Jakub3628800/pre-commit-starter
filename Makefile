.PHONY: run test install build clean

# Variables
UV := uv

run:
	$(UV) run python -m pre_commit_starter

test: install
	$(UV) run pytest tests/ -v

install:
	$(UV) venv --python 3.12 .venv
	$(UV) pip install -e ".[dev]"
	$(UV) run pre-commit install
	@echo "✅ Package installed with development dependencies"

build:
	$(UV) build

clean:
	rm -rf build/ dist/ *.egg-info .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/ .venv
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.py[co]" -delete 2>/dev/null || true

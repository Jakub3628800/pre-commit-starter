.PHONY: run test install build clean

# Variables
VENV := .venv
PYTHON := python3
UV := uv

run:
	$(UV) run python -m pre_commit_starter

test: install
	PYTHONPATH=$(shell pwd) $(VENV)/bin/python -m pytest tests/ -v

install:
	$(PYTHON) -m venv $(VENV) 2>/dev/null || true
	$(UV) pip install -e ".[dev]"
	$(UV) run pre-commit install
	@echo "✅ Package installed with development dependencies"

build:
	$(UV) build

clean:
	rm -rf build/ dist/ *.egg-info .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/ $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.py[co]" -delete 2>/dev/null || true

.PHONY: help install dev-install test lint type-check coverage clean pre-commit update-hooks docs build release check-all setup generate update changelog cleanup

VENV := .venv
PYTHON := python3
UV := uv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
PRE_COMMIT := $(VENV)/bin/pre-commit

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

$(VENV)/bin/activate: pyproject.toml
	$(PYTHON) -m venv $(VENV)
	$(UV) pip install -e ".[dev]"
	$(PRE_COMMIT) install

install: $(VENV)/bin/activate  ## Install package
	$(PIP) install -e .
	$(PRE_COMMIT) install

dev-install: $(VENV)/bin/activate  ## Install package in development mode with all dependencies
	$(PIP) install -e ".[dev]"
	$(PRE_COMMIT) install

test: dev-install  ## Run tests
	$(PYTEST) tests/ -v --cov=src --cov-report=term-missing

lint: dev-install  ## Run linting checks
	$(VENV)/bin/ruff check src/ tests/
	$(VENV)/bin/black --check src/ tests/
	$(VENV)/bin/isort --check-only src/ tests/

type-check: dev-install  ## Run type checking
	$(VENV)/bin/mypy src/ tests/

coverage: dev-install  ## Generate coverage report
	$(PYTEST) tests/ --cov=src --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

clean:  ## Clean up build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

pre-commit: dev-install  ## Generate pre-commit config and install hooks
	$(VENV)/bin/pre-commit-starter --force
	$(PRE_COMMIT) install

update-hooks: dev-install  ## Update pre-commit hooks
	$(PRE_COMMIT) autoupdate
	$(PRE_COMMIT) clean
	$(PRE_COMMIT) install

docs: dev-install  ## Generate documentation
	$(VENV)/bin/pdoc --html --output-dir docs/ src/
	@echo "Documentation generated in docs/index.html"

build: dev-install  ## Build package
	$(VENV)/bin/build

release: check-all  ## Create a new release
	@echo "Creating new release..."
	@read -p "Version: " version; \
	git tag -a $$version -m "Release $$version"; \
	git push origin $$version

check-all: lint type-check test  ## Run all checks

setup: clean dev-install pre-commit  ## Setup development environment

generate:  ## Generate pre-commit configuration
	$(PYTHON) -m src.main

update: update-hooks  ## Update pre-commit hooks (alias for update-hooks)

changelog:  ## Generate changelog from git commits
	$(PYTHON) scripts/generate_changelog.py

cleanup:  ## Remove Python cache files and test artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".hypothesis" -exec rm -rf {} +
	rm -f .coverage
	@echo "Cleanup completed"

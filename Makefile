.PHONY: help install test test-all coverage clean build run-precommit act-check act-test act-list act-run act-pr act-push act-install

# Variables
VENV := .venv
PYTHON := python3
UV := uv
PIP := $(UV) pip
PRE_COMMIT := $(UV) run pre-commit
ACT := act

# Default target
help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Environment Setup & Installation
$(VENV)/bin/activate: pyproject.toml
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created. Activate with 'source $(VENV)/bin/activate'"

install: $(VENV)/bin/activate  ## Install package, dependencies, and pre-commit hooks
	$(UV) pip install -e ".[dev]"
	$(PRE_COMMIT) install
	@echo "Development dependencies installed. Run 'source $(VENV)/bin/activate' to activate."

# Testing
test: install  ## Run tests with pytest using the venv python and project root in PYTHONPATH
	PYTHONPATH=$(shell pwd)/src $(VENV)/bin/python -m pytest src/tests/
	$(PRE_COMMIT) run --all-files

test-all: test  ## Run all tests including GitHub Actions (if act is available)
	@if command -v $(ACT) >/dev/null 2>&1; then \
		echo "Running GitHub Actions tests with act..."; \
		$(ACT) --dry-run || echo "GitHub Actions test failed, but continuing..."; \
	else \
		echo "act not installed - skipping GitHub Actions tests. Run 'make act-install' to enable."; \
	fi

coverage: install  ## Generate coverage report using the venv python and project root in PYTHONPATH
	PYTHONPATH=$(shell pwd)/src $(VENV)/bin/python -m pytest src/tests/ --cov=src/pre_commit_starter --cov-report=term-missing --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

# Pre-commit
run-precommit: install ## Run all pre-commit hooks on all files
	$(PRE_COMMIT) run --all-files

# GitHub Actions Testing with act
act-check:  ## Check if act is installed
	@command -v $(ACT) >/dev/null 2>&1 || { echo >&2 "act is not installed. Run 'make act-install' or install from https://github.com/nektos/act"; exit 1; }
	@echo "act is installed and ready to use"

act-install:  ## Install act (GitHub Actions runner)
	@echo "Installing act..."
	@if command -v curl >/dev/null 2>&1; then \
		curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash; \
	else \
		echo "curl not found. Please install act manually from https://github.com/nektos/act"; \
		exit 1; \
	fi
	@echo "act installed successfully"

act-list: act-check  ## List all GitHub Actions workflows
	$(ACT) -l

act-test: act-check  ## Run all GitHub Actions workflows locally with act
	$(ACT) --dry-run
	@echo "To run workflows for real, use: make act-run"

act-run: act-check  ## Run all GitHub Actions workflows locally (for real)
	$(ACT)

act-pr: act-check  ## Test pull request workflows locally
	$(ACT) pull_request

act-push: act-check  ## Test push workflows locally
	$(ACT) push

# Cleaning
clean:  ## Clean up build artifacts, cache, and virtual environment
	rm -rf build/ dist/ *.egg-info .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/ $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	@echo "Cleaned up build artifacts, cache, and virtual environment."

# Build
build: install  ## Build package
	$(UV) run python -m build

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup and Installation
```bash
make install          # Install package, dependencies, and pre-commit hooks
source .venv/bin/activate  # Activate virtual environment
```

### Testing
```bash
make test            # Run pytest tests and pre-commit hooks
make coverage        # Generate coverage report (outputs to htmlcov/index.html)
make test-all        # Run all tests including GitHub Actions (if act available)
```

### Linting and Formatting
```bash
make run-precommit   # Run all pre-commit hooks on all files
uv run ruff check    # Run ruff linter
uv run ruff format   # Run ruff formatter
```

### Other Commands
```bash
make clean          # Clean build artifacts and virtual environment
make build          # Build package
```

## Architecture Overview

This is a Python CLI tool that auto-generates `.pre-commit-config.yaml` files by detecting technologies in repositories. The architecture follows a modular design:

- **File Scanner** (`src/detector/file_scanner.py`): Scans repository to detect technologies via file extensions and content patterns
- **Hook Registry** (`src/hooks/hook_registry.py`): Maps detected technologies to appropriate pre-commit hooks with priority system
- **YAML Builder** (`src/generator/yaml_builder.py`): Generates the final pre-commit configuration with smart hook merging and ordering
- **CLI Interface** (`src/main.py`): Main entry point using argparse and rich for output formatting

## Key Implementation Details

- Uses uv for package management and virtual environments
- Supports Python 3.9+ with setuptools build system
- Technologies detected: Python, JavaScript, TypeScript, Go, Rust, HTML, CSS, YAML, Docker
- Hook priority system: Security (1) → Basic Checks (2) → Language-Specific (3-4) → Framework-Specific (11) → Performance/Testing (12-14)
- Test fixtures in `src/tests/fixtures/sample_repos/` with expected configs in `src/tests/expected_configs/`
- Rich console output with progress indication and colored text

## Entry Point

The main CLI command is registered as `pre-commit-starter` in pyproject.toml, pointing to `pre_commit_starter.main:main`.

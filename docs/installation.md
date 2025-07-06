# Installation and Usage Guide

## Overview

pre-commit-starter is a CLI tool that automatically detects technologies in your repository and generates an appropriate `.pre-commit-config.yaml` file with relevant hooks.

## Installation Methods

### Method 1: One-time Use with uv (Recommended)

The easiest way to use pre-commit-starter is as a one-time tool with uv:

```bash
uvx --from git+https://github.com/Jakub3628800/pre-commit-starter pre-commit-starter
```

This will:
- Temporarily install the tool
- Run it in your current directory
- Generate a `.pre-commit-config.yaml` file
- Clean up the installation automatically

### Method 2: Install as Persistent Tool with uv

If you plan to use the tool multiple times:

```bash
uv tool install git+https://github.com/Jakub3628800/pre-commit-starter
```

Then run it in any repository:

```bash
pre-commit-starter
```

### Method 3: Development Installation

For contributing or development:

```bash
git clone https://github.com/Jakub3628800/pre-commit-starter
cd pre-commit-starter
make install
```

Then run it:

```bash
make run
# or
python -m pre_commit_starter
```

## Usage

### Basic Usage

Navigate to your repository and run:

```bash
pre-commit-starter
```

This will:
1. Scan your repository for technologies
2. Display detected technologies in a table
3. Ask for your preferences through an interactive interface
4. Generate a `.pre-commit-config.yaml` file with appropriate hooks

### Interactive Configuration

The tool provides an interactive interface that:
- Shows detected technologies
- Asks for confirmation on each technology
- Allows customization of specific hooks
- Uses smart defaults based on your project

### Development Commands

If you're working on the tool itself:

```bash
# Install development dependencies
make install

# Run the tool
make run

# Run tests
make test

# Build package
make build

# Clean up build artifacts
make clean
```

## After Generation

Once the `.pre-commit-config.yaml` file is generated:

1. **Install pre-commit** (if not already installed):
   ```bash
   pip install pre-commit
   # or with uv
   uv tool install pre-commit
   ```

2. **Install the hooks**:
   ```bash
   pre-commit install
   ```

3. **Run hooks on all files** (optional):
   ```bash
   pre-commit run --all-files
   ```

4. **Test the setup**:
   ```bash
   # Make a small change and commit
   git add .
   git commit -m "Test pre-commit hooks"
   ```

## Technology Detection

The tool automatically detects technologies based on:

- **File extensions**: `.py`, `.js`, `.ts`, `.go`, etc.
- **Configuration files**: `package.json`, `go.mod`, `pyproject.toml`, etc.
- **File content**: Import statements, function definitions, etc.

### Supported Technologies

- **Python**:
  - Files: `.py`, `.pyi`, `.pyx`
  - Config: `pyproject.toml`, `requirements.txt`, `setup.py`
  - Tools: Ruff (linting/formatting), MyPy (type checking)
  - Features: uv.lock support, custom MyPy args

- **JavaScript/TypeScript**:
  - Files: `.js`, `.ts`, `.jsx`, `.tsx`
  - Config: `package.json`, `tsconfig.json`
  - Tools: Prettier (formatting), ESLint (linting)
  - Features: TypeScript support, JSX/React detection

- **Go**:
  - Files: `.go`
  - Config: `go.mod`, `go.sum`
  - Tools: golangci-lint, gofmt, goimports
  - Features: Optional go-critic support

- **Docker**:
  - Files: `Dockerfile`, `docker-compose.yml`
  - Tools: hadolint (Dockerfile linting)
  - Features: Large file detection, .dockerignore validation

- **GitHub Actions**:
  - Files: `.github/workflows/*.yml`
  - Tools: actionlint (workflow validation)
  - Features: Security scanning options

- **File Types**:
  - YAML, JSON, TOML, XML syntax checking
  - Trailing whitespace removal
  - End-of-file fixing

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/pre-commit.yml`:

```yaml
name: Pre-commit

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - uses: pre-commit/action@v3.0.0
```

### GitLab CI

Add to `.gitlab-ci.yml`:

```yaml
pre-commit:
  stage: test
  image: python:3.11
  before_script:
    - pip install pre-commit
  script:
    - pre-commit run --all-files
```

## Troubleshooting

For common issues and solutions, see [troubleshooting.md](troubleshooting.md).

## Advanced Usage

### Custom Configuration

You can customize the generated configuration by:

1. Running the tool to generate a base configuration
2. Manually editing the `.pre-commit-config.yaml` file
3. Adding custom hooks or modifying existing ones

### Integration with Existing Workflows

If you already have a `.pre-commit-config.yaml` file, the tool will:
- Detect the existing configuration
- Ask if you want to overwrite it
- Provide guidance on merging configurations

## Getting Help

- Check the [troubleshooting guide](troubleshooting.md)
- Review the [architecture documentation](ARCHITECTURE.md)
- Open an issue on GitHub for bugs or feature requests

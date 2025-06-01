# Installation and Usage Guide

## Overview

pre-commit-starter is a CLI tool that automatically detects technologies in your repository and generates an appropriate `.pre-commit-config.yaml` file with relevant hooks.

## Installation Methods

### Method 1: One-time Use with uv (Recommended)

The easiest way to use pre-commit-starter is as a one-time tool with uv:

```bash
uvx --from git+https://github.com/Jakub3628800/pre-commit-starter pre-commit-starter [--force]
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
pre-commit-starter [options]
```

### Method 3: Traditional pip Installation

```bash
pip install pre-commit-starter
```

Then run it:

```bash
pre-commit-starter [options]
```

### Method 4: Development Installation

For contributing or development:

```bash
git clone https://github.com/Jakub3628800/pre-commit-starter
cd pre-commit-starter
uv sync
uv run pre-commit-starter [options]
```

## Usage

### Basic Usage

Navigate to your repository and run:

```bash
pre-commit-starter
```

This will:
1. Scan your repository for technologies
2. Generate a `.pre-commit-config.yaml` file with appropriate hooks
3. Display a summary of detected technologies and configured hooks

### Command Line Options

- `--force`: Overwrite existing `.pre-commit-config.yaml` file
- `--path PATH`: Specify repository path (default: current directory)
- `--verbose`: Enable verbose output
- `--help`: Show help message

### Examples

```bash
# Generate config in current directory
pre-commit-starter

# Force overwrite existing config
pre-commit-starter --force

# Generate config for specific path
pre-commit-starter --path /path/to/repo

# Verbose output
pre-commit-starter --verbose
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

- **File extensions**: `.py`, `.js`, `.ts`, `.go`, `.rs`, etc.
- **Configuration files**: `package.json`, `Cargo.toml`, `go.mod`, etc.
- **File content**: Import statements, function definitions, etc.

### Supported Technologies

- **Python**: `.py` files, `requirements.txt`, `pyproject.toml`
- **JavaScript/TypeScript**: `.js`, `.ts`, `.jsx`, `.tsx`, `package.json`
- **React**: JSX files, React imports
- **Vue**: `.vue` files
- **Svelte**: `.svelte` files
- **Go**: `.go` files, `go.mod`
- **Rust**: `.rs` files, `Cargo.toml`
- **HTML**: `.html`, `.htm` files
- **CSS**: `.css`, `.scss`, `.sass`, `.less` files
- **And more...**

## Configuration Profiles

The tool includes several built-in profiles:

- **minimal**: Basic hooks for detected technologies
- **standard**: Comprehensive hooks with good defaults
- **strict**: Strict linting and formatting rules
- **security**: Security-focused hooks

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

If you already have a `.pre-commit-config.yaml` file:

- Use `--force` to overwrite it completely
- Or manually merge the generated hooks with your existing configuration

## Performance Tips

- The tool caches detection results for faster subsequent runs
- Use `--path` to limit scanning to specific directories
- Large repositories may take longer to scan initially

## Getting Help

- Check the [troubleshooting guide](troubleshooting.md)
- Review the [architecture documentation](ARCHITECTURE.md)
- Open an issue on GitHub for bugs or feature requests

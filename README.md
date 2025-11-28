# pre-commit-tools

A collection of tools for pre-commit hook management, Python library validation, and CI/CD workflow generation.

## Tools

### 1. pre-commit-tools
Automatically detects technologies in your repository and generates an appropriate `.pre-commit-config.yaml` file with relevant hooks. The generated config includes version tracking metadata for easy regeneration and drift detection.

### 2. check-exports
Validates that non-exported functions aren't imported from outside library boundaries. Features include:
- Warnings for underscore-prefixed exports
- Public submodules support
- Auto-suggestions for fixing violations
- Can be used as a standalone CLI or integrated as a pre-commit hook

### 3. generate-workflow
Generates GitHub Actions workflows for running pre-commit hooks in CI using `uv`. Creates modern workflows that automatically sync with your local pre-commit configuration.

## Quick Start

### Using uv (Recommended)

Generate a pre-commit config:
```bash
uvx --from git+https://github.com/Jakub3628800/pre-commit-tools pre-commit-tools
```

Generate a GitHub Actions workflow:
```bash
uvx --from git+https://github.com/Jakub3628800/pre-commit-tools generate-workflow
```

Validate library exports:
```bash
uvx --from git+https://github.com/Jakub3628800/pre-commit-tools check-exports ./mylib
```

### Using the tool directly

If you have the repository cloned:

```bash
git clone https://github.com/Jakub3628800/pre-commit-tools
cd pre-commit-tools
make install
make run  # Runs pre-commit-tools
```

The `pre-commit-tools` generator will:
1. Scan your repository for technologies (Python, JavaScript, Go, Docker, etc.)
2. Generate a `.pre-commit-config.yaml` file with appropriate hooks and version tracking
3. Guide you through customization options

## After Generation

Install and run pre-commit:

```bash
# Install pre-commit hooks
uvx pre-commit install

# Run on all files
uvx pre-commit run --all-files

# Or use uv run if you have pre-commit in your dependencies
uv run pre-commit run --all-files
```

## Development

### Essential Commands

```bash
# Install development dependencies
make install

# Run the tool
make run

# Run tests
make test

# Build package
make build

# Clean up
make clean
```

### Supported Technologies

- **Python**: Ruff (linting/formatting) + Pyrefly (type checking) + check-exports (optional library validation)
- **JavaScript/TypeScript**: Prettier + ESLint
- **Go**: golangci-lint + formatting
- **Docker**: hadolint for Dockerfile linting
- **GitHub Actions**: actionlint for workflow validation
- **File Types**: YAML, JSON, TOML, XML syntax checking

## Documentation

For detailed installation methods, usage examples, and advanced configuration:

📖 **[Installation and Usage Guide](docs/installation.md)**

Other documentation:
- [Architecture](docs/ARCHITECTURE.md)
- [Troubleshooting](docs/troubleshooting.md)

## License

MIT License - see LICENSE file for details

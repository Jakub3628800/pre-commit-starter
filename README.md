# pre-commit-starter

A CLI tool that automatically detects technologies in your repository and generates an appropriate `.pre-commit-config.yaml` file with relevant hooks.

## Quick Start

### Using uv (Recommended)

Run once in your repository:

```bash
uvx --from git+https://github.com/Jakub3628800/pre-commit-starter pre-commit-starter
```

### Using the tool directly

If you have the repository cloned:

```bash
git clone https://github.com/Jakub3628800/pre-commit-starter
cd pre-commit-starter
make install
make run
```

This will:
1. Scan your repository for technologies (Python, JavaScript, Go, Docker, etc.)
2. Generate a `.pre-commit-config.yaml` file with appropriate hooks
3. Guide you through customization options

## After Generation

Install and run pre-commit:

```bash
# Install pre-commit
pip install pre-commit
# or
uvx --from pre-commit pre-commit install

# Run on all files
pre-commit run --all-files
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

- **Python**: Ruff (linting/formatting) + MyPy (type checking)
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

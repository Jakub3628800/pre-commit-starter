# pre-commit-starter

A starter CLI tool for pre-commit configurations.

## Usage

### With uv

```bash
# Run once without installing (replace <repo_url> with actual URL)
uvx --from git+<repo_url> pre-commit-starter [--force]

# Install as a persistent tool (replace <repo_url> with actual URL)
uv tool install git+<repo_url>
```

### Standard Installation & Usage

```bash
# Install
pip install pre-commit-starter

# Run in your repository
pre-commit-starter

# Install pre-commit hooks
pre-commit install
pre-commit run --all-files
```

## Options

- `--force`: Overwrite existing `.pre-commit-config.yaml`
- `--path`: Specify repository path (default: current directory)

## GitHub Action

Use `.github/workflows/pre-commit-starter-check.yml` for CI integration to enforce checks.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

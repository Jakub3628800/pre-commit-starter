# pre-commit-starter

A starter CLI tool for pre-commit configurations.

## Usage

### With uv

```bash
# Run once without installing
uvx --from git+https://github.com/Jakub3628800/pre-commit-starter pre-commit-starter [--force]
```

```bash
# Install as a persistent tool
uv tool install git+https://github.com/Jakub3628800/pre-commit-starter
```

### Standard Installation & Usage

```bash
# Install
pip install pre-commit-starter
```

```bash
# Run in your repository
pre-commit-starter
```

```bash
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

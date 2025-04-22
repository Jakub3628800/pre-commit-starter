# prec-hook-autodetect

A smart CLI tool that automatically generates comprehensive pre-commit configurations based on repository content.

## Using with uv

```bash
# Run directly without installing
uvx --from git+https://github.com/Jakub3628800/pre-commit-autodetect prec-hook-autodetect

# With force option to overwrite existing config
uvx --from git+https://github.com/Jakub3628800/pre-commit-autodetect prec-hook-autodetect --force

# Install as a persistent tool
uv tool install git+https://github.com/Jakub3628800/pre-commit-autodetect

# Run with specific Python version
uvx --python 3.10 --from git+https://github.com/Jakub3628800/pre-commit-autodetect prec-hook-autodetect
```

For more information about uv tool usage, see the [uv documentation](https://docs.astral.sh/uv/guides/tools/).

## Features

- Automatically detects technologies in your codebase
- Generates optimized pre-commit configurations
- Supports Python, JavaScript/TypeScript, Go, Rust, Terraform, Docker, and more
- Prioritizes security checks, formatting, linting, and other quality tools
- Allows custom hooks via `.prec-hook-autodetect-hooks.yaml`

## Standard Installation

```bash
# Install package
pip install prec-hook-autodetect

# Run in repository
prec-hook-autodetect

# Install hooks
pre-commit install
pre-commit run --all-files
```

## Options

- `--path`: Specify repository path (default: current directory)
- `--force`: Overwrite existing pre-commit config

## GitHub Action

Include `.github/workflows/prec-hook-autodetect-check.yml` for CI integration that:

- Runs on pushes and PRs to main branches
- Generates fresh configs based on repository content
- Ensures consistent code quality across contributions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

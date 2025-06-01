# pre-commit-starter

A CLI tool that automatically detects technologies in your repository and generates an appropriate `.pre-commit-config.yaml` file with relevant hooks.

## Quick Start

Run once in your repository with uv:

```bash
uvx --from git+https://github.com/Jakub3628800/pre-commit-starter pre-commit-starter
```

This will scan your repository, detect technologies (Python, JavaScript, Go, Rust, etc.), and generate a `.pre-commit-config.yaml` file with appropriate hooks.

Then install and run pre-commit:

```bash
uvx pre-commit install
uvx pre-commit run --all-files
```

## Options

- `--force`: Overwrite existing `.pre-commit-config.yaml`
- `--path PATH`: Specify repository path (default: current directory)

## Documentation

For detailed installation methods, usage examples, and advanced configuration:

📖 **[Installation and Usage Guide](docs/installation.md)**

Other documentation:
- [Architecture](docs/ARCHITECTURE.md)
- [Troubleshooting](docs/troubleshooting.md)

## License

MIT License - see LICENSE file for details

# Troubleshooting Guide

## Common Issues

### 1. Hook Installation Failures

#### Problem: Hook installation fails with dependency errors

```
[ERROR] Hook `hook-id` failed to install
```

**Solution:**

1. Try updating pre-commit first:
   ```bash
   pre-commit autoupdate
   ```
2. Check if the hook requires system dependencies
3. Verify your Python version matches requirements

### 2. Pre-commit Taking Too Long

#### Problem: Hooks are running slowly

**Solution:**

1. Use `--hook-stage` to run specific hooks:
   ```bash
   pre-commit run --hook-stage commit
   ```
2. Consider skipping heavy hooks with `SKIP`:
   ```bash
   SKIP=mypy pre-commit run
   ```

### 3. Technology Detection Issues

#### Problem: Missing technology detection

**Solution:**

1. Check if your files are in standard locations
2. Run the tool directly to see detection results:
   ```bash
   python -m pre_commit_starter
   ```
3. Check supported technology patterns in documentation

### 4. Configuration Generation Issues

#### Problem: Tool fails to generate configuration

**Solution:**

1. Ensure you're running from the root of your repository
2. Check file permissions in your project directory
3. Try running with development installation:
   ```bash
   git clone https://github.com/Jakub3628800/pre-commit-starter
   cd pre-commit-starter
   make install
   make run
   ```

### 5. Common Error Messages

#### `ModuleNotFoundError: No module named 'pre_commit_starter'`

- Install the package properly:
  ```bash
  make install
  ```
- Or use uv for one-time execution:
  ```bash
  uvx --from git+https://github.com/Jakub3628800/pre-commit-starter pre-commit-starter
  ```

#### `Permission denied` errors

- Check file permissions in your project directory
- Ensure you have write access to create `.pre-commit-config.yaml`

#### `YAML syntax error` in generated config

- This shouldn't happen with template-based generation
- If it does, please report it as a bug
- As a workaround, manually fix the YAML syntax

### 6. Development Issues

#### Problem: Tests failing after changes

**Solution:**

1. Clean and reinstall dependencies:
   ```bash
   make clean
   make install
   ```

2. Run tests to identify issues:
   ```bash
   make test
   ```

3. Check if new dependencies are needed in `pyproject.toml`

#### Problem: Import errors in development

**Solution:**

1. Ensure you're in the project root directory
2. Check that the virtual environment is activated:
   ```bash
   source .venv/bin/activate
   ```
3. Reinstall in development mode:
   ```bash
   make install
   ```

### 7. Pre-commit Hook Issues

#### Problem: Hooks not running on commit

**Solution:**

1. Ensure pre-commit is installed:
   ```bash
   pre-commit install
   ```

2. Check that `.pre-commit-config.yaml` exists and is valid:
   ```bash
   pre-commit validate-config
   ```

3. Test hooks manually:
   ```bash
   pre-commit run --all-files
   ```

#### Problem: Specific hooks failing

**Solution:**

1. Check hook-specific requirements (e.g., Node.js for ESLint)
2. Update hook versions:
   ```bash
   pre-commit autoupdate
   ```
3. Check hook documentation for system requirements

### 8. Tool-Specific Issues

#### Ruff Issues
- Ensure you have the latest version of ruff
- Check `pyproject.toml` for conflicting configurations
- Ruff replaces flake8 in this project

#### MyPy Issues
- Ensure all dependencies are installed
- Check for missing type stubs
- MyPy configuration is in `pyproject.toml`

#### ESLint/Prettier Issues
- Ensure Node.js is installed
- Check for conflicting configuration files
- Consider using `npm install` in your project

### 9. Best Practices

1. Always run from the project root directory
2. Use `make install` for development setup
3. Keep hooks up to date with `pre-commit autoupdate`
4. Test configuration before committing with `pre-commit run --all-files`

### 10. Getting Help

If you encounter issues not addressed in this guide:

1. Check the [GitHub Issues](https://github.com/Jakub3628800/pre-commit-starter/issues)
2. Include the following information when reporting issues:
   - Operating system and version
   - Python version
   - Error messages (full traceback)
   - Steps to reproduce
   - Project structure (if relevant)

## Quick Reference

### Essential Commands

```bash
# Development setup
make install          # Install dependencies
make run             # Run the tool
make test            # Run tests
make build           # Build package
make clean           # Clean artifacts

# Pre-commit commands
pre-commit install                 # Install hooks
pre-commit run --all-files        # Run all hooks
pre-commit autoupdate             # Update hook versions
SKIP=hook-id git commit -m "msg"  # Skip specific hook
```

### Debug Commands

```bash
# Check tool installation
python -m pre_commit_starter --help

# Validate pre-commit config
pre-commit validate-config

# Run specific hook
pre-commit run hook-id

# Check hook versions
pre-commit autoupdate --dry-run
```

### File Structure Check

Your project should have:
- `.pre-commit-config.yaml` (generated by the tool)
- `.git/` directory (must be a git repository)
- Source files in standard locations (e.g., `src/`, root directory)

## Reporting Issues

When reporting issues, please include:

1. **System Information**:
   - OS and version
   - Python version
   - Tool version or commit hash

2. **Error Details**:
   - Full error message
   - Command that caused the error
   - Expected vs actual behavior

3. **Project Context**:
   - Repository structure
   - Technology stack
   - Any relevant configuration files

4. **Steps to Reproduce**:
   - Minimal example if possible
   - Exact commands used
   - Any relevant files or configurations

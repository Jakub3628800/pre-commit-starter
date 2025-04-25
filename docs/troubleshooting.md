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
   make update
   # or
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
   SKIP=pylint pre-commit run
   ```

### 3. Technology Detection Issues

#### Problem: Missing technology detection

**Solution:**

1. Check if your files are in standard locations
2. Run with verbose output:
   ```bash
   python -m src.main --path . --verbose
   ```
3. Check supported technology patterns in documentation

### 4. Configuration Conflicts

#### Problem: Conflicting hook configurations

**Solution:**

1. Check for duplicate hook entries
2. Remove existing `.pre-commit-config.yaml`
3. Regenerate with:
   ```bash
   make generate
   ```

### 5. Common Error Messages

#### `ValueError: Repo unknown`

- Ensure hook repository URLs are correct
- Try running `pre-commit autoupdate`

#### `ModuleNotFoundError`

- Install development dependencies:
  ```bash
  make install
  ```

#### `Permission denied`

- Check file permissions
- Run with appropriate permissions

#### `error: look-behind requires fixed-width pattern`

- This is a regex error that can occur in Python regex patterns
- The issue has been fixed in recent versions by replacing look-behind assertions with simpler patterns
- If you encounter this, update to the latest version or simplify your regex patterns

### 6. Best Practices

1. Always run `make update` after pulling changes
2. Use `make lint` before committing
3. Check hook documentation for specific requirements
4. Keep hooks up to date with `pre-commit autoupdate`

### 7. Getting Help

If you encounter issues not addressed in this guide:

1. Check the [GitHub Issues](https://github.com/yourusername/pre-commit-starter/issues)
2. Run with `--verbose` flag for detailed output
3. Include error messages and debug logs when reporting issues

## Quick Reference

### Common Commands

```bash
# Install dependencies and hooks
make install

# Generate new configuration
make generate

# Update hooks
make update

# Run specific hooks
pre-commit run hook-id

# Skip specific hooks
SKIP=hook-id git commit -m "message"
```

### Debug Commands

```bash
# Run with verbose output
python -m src.main --verbose

# Check hook versions
pre-commit autoupdate --dry-run

# Clean and reinstall
make clean && make install
```

### Reporting Issues

If you encounter a problem that isn't covered here, please report it:

1. Check the [GitHub Issues](https://github.com/yourusername/pre-commit-starter/issues) for similar problems.
2. If your issue is new, [create a new issue](https://github.com/yourusername/pre-commit-starter/issues/new).
3. Provide the following information:

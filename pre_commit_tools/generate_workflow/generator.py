"""Generate GitHub Actions workflow from pre-commit config."""

from pathlib import Path
from typing import Optional

import yaml


def parse_precommit_config(config_path: Path) -> dict:
    """Parse .pre-commit-config.yaml and extract metadata.

    Args:
        config_path: Path to .pre-commit-config.yaml

    Returns:
        Dict with parsed config metadata
    """
    with open(config_path) as f:
        config = yaml.safe_load(f)

    python_version = None
    if "default_language_version" in config:
        python_ver = config["default_language_version"].get("python")
        if python_ver:
            # Extract version like "3.14" from "python3.14"
            python_version = python_ver.replace("python", "")

    return {
        "python_version": python_version or "3.11",  # Default to 3.11
    }


def generate_workflow(
    output_path: Optional[Path] = None,
    config_path: Optional[Path] = None,
    main_branch: str = "main",
) -> str:
    """Generate GitHub Actions workflow for pre-commit.

    Args:
        output_path: Where to write the workflow file (if None, returns string)
        config_path: Path to .pre-commit-config.yaml (if None, uses default)
        main_branch: Main branch name (default: "main")

    Returns:
        Generated workflow YAML as string
    """
    if config_path is None:
        config_path = Path(".pre-commit-config.yaml")

    metadata = {}
    if config_path.exists():
        metadata = parse_precommit_config(config_path)
    else:
        # Use defaults if no config found
        metadata = {"python_version": "3.11"}

    workflow = f"""---
name: pre-commit

on:
  push:
    branches: [ {main_branch} ]
  pull_request:
    branches: [ {main_branch} ]

env:
  SKIP: no-commit-to-branch  # Disable the no-commit-to-branch hook in CI

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '{metadata["python_version"]}'

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - name: Run pre-commit hooks
        run: uvx pre-commit run --all-files --show-diff-on-failure
"""

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(workflow)

    return workflow

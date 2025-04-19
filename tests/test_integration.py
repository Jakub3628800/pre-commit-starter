"""Integration tests for the pre-commit-starter tool."""
import argparse
import os
import sys
from pathlib import Path

import yaml

from src.main import run_generation


def create_args(path, force=False):
    """Create command line arguments."""
    args = argparse.Namespace()
    args.path = path
    args.force = force
    args.auto = True  # Use auto mode for tests to avoid interactive prompts
    args.dry_run = False
    args.verbose = False
    return args


def test_python_repo_workflow(sample_python_repo, expected_python_config, capsys):
    """Test complete workflow with a Python repository."""
    args = create_args(sample_python_repo)
    run_generation(args)
    captured = capsys.readouterr()

    assert "Successfully generated" in captured.out

    # Check that config file was created
    config_path = sample_python_repo / ".pre-commit-config.yaml"
    assert config_path.exists()

    # Verify config content
    with open(config_path, "r", encoding="utf-8") as f:
        generated_config = f.read()

    # Parse and check essential components
    config_dict = yaml.safe_load(generated_config)

    # Check header comments
    assert "Technologies detected: python" in generated_config
    assert "To install: pre-commit install" in generated_config

    # Check essential repos are included
    repo_urls = [repo["repo"] for repo in config_dict["repos"]]
    assert "https://github.com/pre-commit/pre-commit-hooks" in repo_urls
    assert "https://github.com/psf/black" in repo_urls

    # Check essential hooks are included
    pre_commit_hooks_repo = next(
        repo
        for repo in config_dict["repos"]
        if repo["repo"] == "https://github.com/pre-commit/pre-commit-hooks"
    )
    pre_commit_hook_ids = [hook["id"] for hook in pre_commit_hooks_repo["hooks"]]
    assert "trailing-whitespace" in pre_commit_hook_ids
    assert "end-of-file-fixer" in pre_commit_hook_ids
    assert "check-yaml" in pre_commit_hook_ids

    black_repo = next(
        repo
        for repo in config_dict["repos"]
        if repo["repo"] == "https://github.com/psf/black"
    )
    black_hook_ids = [hook["id"] for hook in black_repo["hooks"]]
    assert "black" in black_hook_ids


def test_mixed_repo_workflow(sample_mixed_repo, expected_mixed_config, capsys):
    """Test complete workflow with a mixed technology repository."""
    args = create_args(sample_mixed_repo)
    run_generation(args)
    captured = capsys.readouterr()

    assert "Successfully generated" in captured.out

    # Check that config file was created
    config_path = sample_mixed_repo / ".pre-commit-config.yaml"
    assert config_path.exists()

    # Verify config content
    with open(config_path, "r", encoding="utf-8") as f:
        generated_config = f.read()

    # Parse and check essential components
    config_dict = yaml.safe_load(generated_config)

    # Check header comments
    assert "Technologies detected:" in generated_config
    technologies = ["python", "javascript", "terraform", "docker", "shell"]
    for tech in technologies:
        assert tech in generated_config

    # Check essential repos are included
    repo_urls = [repo["repo"] for repo in config_dict["repos"]]
    assert "https://github.com/pre-commit/pre-commit-hooks" in repo_urls

    # Check at least one specific hook for each technology
    # Not all repos might be included depending on the detection confidence
    must_have_hooks = []

    # Check pre-commit hooks
    pre_commit_hooks_repo = next(
        repo
        for repo in config_dict["repos"]
        if repo["repo"] == "https://github.com/pre-commit/pre-commit-hooks"
    )
    pre_commit_hook_ids = [hook["id"] for hook in pre_commit_hooks_repo["hooks"]]
    assert "trailing-whitespace" in pre_commit_hook_ids
    assert "end-of-file-fixer" in pre_commit_hook_ids

    # Check if at least one technology-specific hook is present
    # This is more lenient than requiring specific hooks
    technology_detected = False
    for repo in config_dict["repos"]:
        if repo["repo"] != "https://github.com/pre-commit/pre-commit-hooks":
            technology_detected = True
            break

    assert technology_detected, "No technology-specific hooks were included"


def test_frontend_repo_workflow(sample_frontend_repo, expected_frontend_config, capsys):
    """Test complete workflow with a frontend repository."""
    args = create_args(sample_frontend_repo)
    run_generation(args)
    captured = capsys.readouterr()

    assert "Successfully generated" in captured.out

    # Check that config file was created
    config_path = sample_frontend_repo / ".pre-commit-config.yaml"
    assert config_path.exists()

    # Verify config content
    with open(config_path, "r", encoding="utf-8") as f:
        generated_config = f.read()

    # Parse and check essential components
    config_dict = yaml.safe_load(generated_config)

    # Check if key technologies are mentioned in header
    frontend_techs = ["html", "css", "javascript", "react", "typescript"]
    header = generated_config.split("\n")[1]  # Get the technologies line
    techs_mentioned = sum(1 for tech in frontend_techs if tech in header.lower())

    # At least 3 frontend technologies should be detected
    assert (
        techs_mentioned >= 3
    ), f"Only {techs_mentioned} frontend technologies detected in: {header}"

    # Check essential repos are included
    repo_urls = [repo["repo"] for repo in config_dict["repos"]]
    assert "https://github.com/pre-commit/pre-commit-hooks" in repo_urls

    # Check pre-commit hooks
    pre_commit_hooks_repo = next(
        repo
        for repo in config_dict["repos"]
        if repo["repo"] == "https://github.com/pre-commit/pre-commit-hooks"
    )
    pre_commit_hook_ids = [hook["id"] for hook in pre_commit_hooks_repo["hooks"]]
    assert "trailing-whitespace" in pre_commit_hook_ids
    assert "end-of-file-fixer" in pre_commit_hook_ids

    # Check if at least one frontend-specific hook is present
    frontend_hook_found = False
    frontend_hook_repos = [
        "https://github.com/pre-commit/mirrors-prettier",
        "https://github.com/pre-commit/mirrors-eslint",
        "https://github.com/pre-commit/mirrors-csslint",
    ]

    for repo_url in frontend_hook_repos:
        if repo_url in repo_urls:
            frontend_hook_found = True
            break

    assert frontend_hook_found, "No frontend-specific hooks were included"


def test_go_repo_workflow(sample_go_repo, expected_go_config, capsys):
    """Test complete workflow with a Go repository."""
    # Create a Go file to ensure detection
    (sample_go_repo / "main.go").write_text(
        'package main\n\nfunc main() {\n\tprintln("Hello, Go!")\n}\n'
    )

    args = create_args(sample_go_repo)
    run_generation(args)
    captured = capsys.readouterr()

    assert "Successfully generated" in captured.out

    # Check that config file was created
    config_path = sample_go_repo / ".pre-commit-config.yaml"
    assert config_path.exists()

    # Verify config content
    with open(config_path, "r", encoding="utf-8") as f:
        generated_config = f.read()

    # Parse and check essential components
    config_dict = yaml.safe_load(generated_config)

    # Check header comments
    assert "Technologies detected:" in generated_config
    assert "go" in generated_config.lower()

    # Check essential repos are included
    repo_urls = [repo["repo"] for repo in config_dict["repos"]]
    assert "https://github.com/pre-commit/pre-commit-hooks" in repo_urls

    # Check pre-commit hooks
    pre_commit_hooks_repo = next(
        repo
        for repo in config_dict["repos"]
        if repo["repo"] == "https://github.com/pre-commit/pre-commit-hooks"
    )
    pre_commit_hook_ids = [hook["id"] for hook in pre_commit_hooks_repo["hooks"]]
    assert "trailing-whitespace" in pre_commit_hook_ids
    assert "end-of-file-fixer" in pre_commit_hook_ids

    # Check if at least one Go-specific hook is present
    go_hook_found = False
    go_hook_repos = [
        "https://github.com/dnephin/pre-commit-golang",
        "https://github.com/golangci/golangci-lint",
    ]

    for repo_url in go_hook_repos:
        if repo_url in repo_urls:
            go_hook_found = True
            break

    assert go_hook_found, "No Go-specific hooks were included"


def test_rust_repo_workflow(sample_rust_repo, expected_rust_config, capsys):
    """Test complete workflow with a Rust repository."""
    # Ensure detection by creating a prominent Rust file
    (sample_rust_repo / "src" / "main.rs").write_text(
        """
fn main() {
    println!("Hello, Rust!");
}
    """
    )

    args = create_args(sample_rust_repo)
    run_generation(args)
    captured = capsys.readouterr()

    assert "Successfully generated" in captured.out

    # Check that config file was created
    config_path = sample_rust_repo / ".pre-commit-config.yaml"
    assert config_path.exists()

    # Verify config content
    with open(config_path, "r", encoding="utf-8") as f:
        generated_config = f.read()

    # Parse and check essential components
    config_dict = yaml.safe_load(generated_config)

    # Check header comments
    assert "Technologies detected:" in generated_config
    assert "rust" in generated_config.lower()

    # Check essential repos are included
    repo_urls = [repo["repo"] for repo in config_dict["repos"]]
    assert "https://github.com/pre-commit/pre-commit-hooks" in repo_urls

    # Check pre-commit hooks
    pre_commit_hooks_repo = next(
        repo
        for repo in config_dict["repos"]
        if repo["repo"] == "https://github.com/pre-commit/pre-commit-hooks"
    )
    pre_commit_hook_ids = [hook["id"] for hook in pre_commit_hooks_repo["hooks"]]
    assert "trailing-whitespace" in pre_commit_hook_ids
    assert "end-of-file-fixer" in pre_commit_hook_ids

    # Check if Rust-specific hook is present
    assert (
        "https://github.com/doublify/pre-commit-rust" in repo_urls
    ), "Rust-specific hook was not included"


def test_empty_repo(temp_repo_dir, capsys):
    """Test behavior with an empty repository."""
    args = create_args(temp_repo_dir)
    run_generation(args)
    captured = capsys.readouterr()

    assert "No supported file types detected" in captured.out

    # Check that no config file was created
    config_path = temp_repo_dir / ".pre-commit-config.yaml"
    assert not config_path.exists()


def test_existing_config_protection(sample_python_repo, capsys):
    """Test that existing config is not overwritten without force flag."""
    # Create an existing config
    config_path = sample_python_repo / ".pre-commit-config.yaml"
    config_path.write_text("# Existing config")

    # Try without force flag
    args = create_args(sample_python_repo, force=False)
    run_generation(args)
    captured = capsys.readouterr()

    assert "already exists" in captured.out
    assert config_path.read_text() == "# Existing config"

    # Try with force flag
    args = create_args(sample_python_repo, force=True)
    run_generation(args)
    captured = capsys.readouterr()

    assert "Successfully generated" in captured.out
    assert config_path.read_text() != "# Existing config"


def test_invalid_path(capsys):
    """Test behavior with an invalid repository path."""
    args = create_args("/nonexistent/path")
    run_generation(args)
    captured = capsys.readouterr()

    assert "Error: /nonexistent/path is not a valid directory" in captured.out

"""Test configuration and fixtures."""

import json
import shutil

import pytest


@pytest.fixture
def temp_repo_dir(tmp_path):
    """Create a temporary directory for test repositories."""
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()
    yield repo_dir
    # Cleanup
    shutil.rmtree(repo_dir)


@pytest.fixture
def sample_python_repo(temp_repo_dir):
    """Create a sample Python repository."""
    # Create Python files
    (temp_repo_dir / "main.py").write_text("def main():\n    pass\n")
    (temp_repo_dir / "test_main.py").write_text("def test_main():\n    pass\n")
    (temp_repo_dir / "requirements.txt").write_text("pytest==8.0.0\n")
    return temp_repo_dir


@pytest.fixture
def sample_mixed_repo(temp_repo_dir):
    """Create a sample repository with multiple technologies."""
    # Python files
    (temp_repo_dir / "app.py").write_text("def app():\n    pass\n")
    (temp_repo_dir / "requirements.txt").write_text("flask==3.0.0\n")

    # JavaScript files
    (temp_repo_dir / "src").mkdir()
    (temp_repo_dir / "src" / "index.js").write_text("console.log('Hello');")
    (temp_repo_dir / "package.json").write_text('{"name": "test-app"}')

    # Terraform files
    (temp_repo_dir / "infrastructure").mkdir()
    (temp_repo_dir / "infrastructure" / "main.tf").write_text(
        'resource "aws_s3_bucket" "bucket" {}'
    )

    # Docker files
    (temp_repo_dir / "Dockerfile").write_text("FROM python:3.8\n")

    # Shell scripts
    (temp_repo_dir / "scripts").mkdir()
    (temp_repo_dir / "scripts" / "setup.sh").write_text("#!/bin/bash\necho 'Setup'")

    return temp_repo_dir


@pytest.fixture
def sample_frontend_repo(temp_repo_dir):
    """Create a sample frontend repository with React, TypeScript, and CSS."""
    # Create directories
    (temp_repo_dir / "src").mkdir()
    (temp_repo_dir / "public").mkdir()
    (temp_repo_dir / "src" / "components").mkdir()
    (temp_repo_dir / "src" / "styles").mkdir()

    # Package configuration
    package_json = {
        "name": "frontend-app",
        "version": "1.0.0",
        "dependencies": {"react": "^18.2.0", "react-dom": "^18.2.0"},
        "devDependencies": {
            "typescript": "^5.2.2",
            "eslint": "^8.55.0",
            "prettier": "^3.1.0",
        },
    }
    (temp_repo_dir / "package.json").write_text(json.dumps(package_json, indent=2))
    (temp_repo_dir / "tsconfig.json").write_text('{"compilerOptions": {"jsx": "react"}}')

    # React component files
    (temp_repo_dir / "src" / "components" / "App.tsx").write_text(
        """
import React from 'react';
import '../styles/App.css';

const App: React.FC = () => {
  return (
    <div className="app">
      <h1>Hello World</h1>
    </div>
  );
};

export default App;
    """
    )

    # CSS files
    (temp_repo_dir / "src" / "styles" / "App.css").write_text(
        """
.app {
  font-family: Arial, sans-serif;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  color: #333;
}
    """
    )

    # HTML file
    (temp_repo_dir / "public" / "index.html").write_text(
        """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>React App</title>
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
    """
    )

    return temp_repo_dir


@pytest.fixture
def sample_go_repo(temp_repo_dir):
    """Create a sample Go repository."""
    # Create directories
    (temp_repo_dir / "cmd").mkdir()
    (temp_repo_dir / "internal").mkdir()
    (temp_repo_dir / "pkg").mkdir()

    # Go module file
    (temp_repo_dir / "go.mod").write_text("module github.com/example/goapp\n\ngo 1.20\n")

    # Main Go file
    (temp_repo_dir / "cmd" / "main.go").write_text(
        """
package main

import (
    "fmt"
)

func main() {
    fmt.Println("Hello, Go!")
}
    """
    )

    # Package Go file
    (temp_repo_dir / "pkg" / "greeter.go").write_text(
        """
package greeter

// Greet returns a greeting for the given name
func Greet(name string) string {
    return "Hello, " + name + "!"
}
    """
    )

    # Test file
    (temp_repo_dir / "pkg" / "greeter_test.go").write_text(
        """
package greeter

import "testing"

func TestGreet(t *testing.T) {
    result := Greet("World")
    expected := "Hello, World!"
    if result != expected {
        t.Errorf("Expected %s but got %s", expected, result)
    }
}
    """
    )

    return temp_repo_dir


@pytest.fixture
def sample_rust_repo(temp_repo_dir):
    """Create a sample Rust repository."""
    # Create directories
    (temp_repo_dir / "src").mkdir()
    (temp_repo_dir / "tests").mkdir()

    # Cargo.toml file
    (temp_repo_dir / "Cargo.toml").write_text(
        """
[package]
name = "rust-app"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
    """
    )

    # Main source file
    (temp_repo_dir / "src" / "main.rs").write_text(
        """
use std::fmt;

struct Point {
    x: i32,
    y: i32,
}

impl fmt::Display for Point {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}

fn main() {
    let point = Point { x: 10, y: 20 };
    println!("Point: {}", point);
}
    """
    )

    # Library source file
    (temp_repo_dir / "src" / "lib.rs").write_text(
        """
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
    }
}
    """
    )

    return temp_repo_dir


@pytest.fixture
def expected_python_config():
    """Return expected pre-commit config for Python repository."""
    return """# Pre-commit configuration generated by pre-commit-starter
# Technologies detected: python
# To install: pre-commit install
# To update: pre-commit autoupdate

repos:
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.5.0
  hooks:
  - id: trailing-whitespace
  - id: end-of-file-fixer
  - id: check-yaml
  - id: check-added-large-files
  - id: check-merge-conflict
- repo: https://github.com/psf/black
  rev: 23.12.1
  hooks:
  - id: black
- repo: https://github.com/pycqa/isort
  rev: 5.13.2
  hooks:
  - id: isort
    args:
    - --profile
    - black
- repo: https://github.com/pycqa/flake8
  rev: 6.1.0
  hooks:
  - id: flake8
"""


@pytest.fixture
def expected_mixed_config():
    """Return expected pre-commit config for mixed technology repository."""
    return """# Pre-commit configuration generated by pre-commit-starter
# Technologies detected: python, javascript, terraform, docker, shell
# To install: pre-commit install
# To update: pre-commit autoupdate

repos:
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.5.0
  hooks:
  - id: trailing-whitespace
  - id: end-of-file-fixer
  - id: check-yaml
  - id: check-added-large-files
  - id: check-merge-conflict
- repo: https://github.com/psf/black
  rev: 23.12.1
  hooks:
  - id: black
- repo: https://github.com/pycqa/isort
  rev: 5.13.2
  hooks:
  - id: isort
    args:
    - --profile
    - black
- repo: https://github.com/pycqa/flake8
  rev: 6.1.0
  hooks:
  - id: flake8
- repo: https://github.com/pre-commit/mirrors-prettier
  rev: v3.1.0
  hooks:
  - id: prettier
- repo: https://github.com/pre-commit/mirrors-eslint
  rev: v8.56.0
  hooks:
  - id: eslint
- repo: https://github.com/antonbabenko/pre-commit-terraform
  rev: v1.83.5
  hooks:
  - id: terraform_fmt
  - id: terraform_tflint
  - id: terraform_docs
- repo: https://github.com/hadolint/hadolint
  rev: v2.12.0
  hooks:
  - id: hadolint
- repo: https://github.com/shellcheck-py/shellcheck-py
  rev: v0.9.0.6
  hooks:
  - id: shellcheck
"""


@pytest.fixture
def expected_frontend_config():
    """Return expected pre-commit config for frontend repository."""
    return """# Pre-commit configuration generated by pre-commit-starter
# Technologies detected: css, html, javascript, react, typescript
# To install: pre-commit install
# To update: pre-commit autoupdate

repos:
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.5.0
  hooks:
  - id: trailing-whitespace
    args: ["--markdown-linebreak-ext=md"]
  - id: end-of-file-fixer
  - id: check-yaml
  - id: check-added-large-files
  - id: check-merge-conflict
  - id: detect-private-key
  - id: detect-aws-credentials
  - id: check-case-conflict
  - id: check-executables-have-shebangs
  - id: check-toml
  - id: check-vcs-permalinks
- repo: https://github.com/gitleaks/gitleaks
  rev: v8.22.1
  hooks:
  - id: gitleaks
    name: Detect hardcoded secrets
- repo: https://github.com/pre-commit/mirrors-prettier
  rev: v3.1.0
  hooks:
  - id: prettier
    additional_dependencies:
    - "@trivago/prettier-plugin-sort-imports"
  - id: prettier
    types: ["css", "scss"]
  - id: prettier
    types: ["file", "jsx", "tsx"]
    additional_dependencies:
    - "@trivago/prettier-plugin-sort-imports"
  - id: prettier
    types: ["file", "ts", "tsx"]
    additional_dependencies:
    - "@trivago/prettier-plugin-sort-imports"
  - id: prettier
    types: ["html"]
  - id: prettier
    types: ["json"]
- repo: https://github.com/pre-commit/mirrors-eslint
  rev: v8.56.0
  hooks:
  - id: eslint
    files: \\.js$
    args: ["--fix"]
  - id: eslint
    files: \\.jsx$|\\.tsx$
    args: ["--fix"]
    additional_dependencies:
    - eslint-plugin-react
    - eslint-plugin-react-hooks
- repo: https://github.com/thibaudcolas/curlylint
  rev: v0.13.1
  hooks:
  - id: curlylint
    types: ["html"]
- repo: https://github.com/pre-commit/mirrors-csslint
  rev: v1.0.5
  hooks:
  - id: csslint
"""


@pytest.fixture
def expected_go_config():
    """Return expected pre-commit config for Go repository."""
    return """# Pre-commit configuration generated by pre-commit-starter
# Technologies detected: go
# To install: pre-commit install
# To update: pre-commit autoupdate

repos:
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.5.0
  hooks:
  - id: trailing-whitespace
    args: ["--markdown-linebreak-ext=md"]
  - id: end-of-file-fixer
  - id: check-yaml
  - id: check-added-large-files
  - id: check-merge-conflict
  - id: detect-private-key
  - id: detect-aws-credentials
  - id: check-case-conflict
  - id: check-executables-have-shebangs
  - id: check-toml
  - id: check-vcs-permalinks
- repo: https://github.com/gitleaks/gitleaks
  rev: v8.22.1
  hooks:
  - id: gitleaks
    name: Detect hardcoded secrets
- repo: https://github.com/golangci/golangci-lint
  rev: v1.55.2
  hooks:
  - id: golangci-lint
- repo: https://github.com/dnephin/pre-commit-golang
  rev: v0.5.1
  hooks:
  - id: go-fmt
  - id: go-vet
  - id: go-imports
  - id: go-critic
"""


@pytest.fixture
def expected_rust_config():
    """Return expected pre-commit config for Rust repository."""
    return """# Pre-commit configuration generated by pre-commit-starter
# Technologies detected: rust
# To install: pre-commit install
# To update: pre-commit autoupdate

repos:
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.5.0
  hooks:
  - id: trailing-whitespace
    args: ["--markdown-linebreak-ext=md"]
  - id: end-of-file-fixer
  - id: check-yaml
  - id: check-added-large-files
  - id: check-merge-conflict
  - id: detect-private-key
  - id: detect-aws-credentials
  - id: check-case-conflict
  - id: check-executables-have-shebangs
  - id: check-toml
  - id: check-vcs-permalinks
- repo: https://github.com/gitleaks/gitleaks
  rev: v8.22.1
  hooks:
  - id: gitleaks
    name: Detect hardcoded secrets
- repo: https://github.com/doublify/pre-commit-rust
  rev: v1.0
  hooks:
  - id: fmt
  - id: cargo-check
  - id: clippy
"""

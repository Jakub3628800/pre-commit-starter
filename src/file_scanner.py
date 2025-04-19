"""File scanner module for detecting technologies in a repository."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Dict, Optional, Set, TypedDict


@dataclass
class TechInfo:
    """Information about a detected technology."""

    name: str
    count: int
    version: str | None
    confidence: float  # Confidence score for the detection


class FileScanner:
    """Scans repository and detects technologies based on file types and patterns."""

    TECH_PATTERNS: ClassVar[dict[str, dict]] = {
        "python": {
            "file_patterns": [
                r"\.py$",
                r"\.pyi$",
                r"\.pyx$",
                r"requirements\.txt$",
                r"setup\.py$",
                r"pyproject\.toml$",
            ],
            "content_patterns": [
                r"^import\s+[a-zA-Z_][a-zA-Z0-9_]*",  # Python import (on its own line)
                r"^from\s+[a-zA-Z_][a-zA-Z0-9_.]+\s+import",  # Python from import (on its own line)
                r"def\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(",  # Python function definition
                r"class\s+[a-zA-Z_][a-zA-Z0-9_]*\s*(?:\([^)]*\))?\s*:",  # Python class definition
            ],
            "version_files": ["requirements.txt", "setup.py", "pyproject.toml"],
        },
        "javascript": {
            "file_patterns": [r"\.js$", r"\.jsx$", r"package\.json$", r"\.mjs$"],
            "content_patterns": [
                r"import\s+.*from",
                r"export\s+(default\s+)?(function|class|const)",
                r"require\(",
            ],
            "version_files": ["package.json"],
        },
        "typescript": {
            "file_patterns": [r"\.ts$", r"\.tsx$", r"tsconfig\.json$"],
            "content_patterns": [
                r"interface\s+\w+",
                r"type\s+\w+\s*=",
                r":\s*(string|number|boolean|any)\b",
            ],
            "version_files": ["package.json"],
        },
        "react": {
            "file_patterns": [r"\.jsx$", r"\.tsx$"],
            "content_patterns": [
                r"import\s+.*?React",
                r"React\.Component",
                r"<.*?>",
                r"useState|useEffect|useContext",
            ],
            "version_files": ["package.json"],
        },
        "vue": {
            "file_patterns": [r"\.vue$"],
            "content_patterns": [
                r"<template.*?>",
                r"<script.*?>",
                r"Vue\.component",
                r"createApp",
            ],
            "version_files": ["package.json"],
        },
        "svelte": {
            "file_patterns": [r"\.svelte$"],
            "content_patterns": [r"<script.*?>", r"<style.*?>", r"\$:", r"on:.*?="],
            "version_files": ["package.json"],
        },
        "terraform": {
            "file_patterns": [r"\.tf$", r"\.tfvars$"],
            "content_patterns": [
                r'resource\s+".*?"',
                r'provider\s+".*?"',
                r'variable\s+".*?"',
            ],
            "version_files": [],
        },
        "docker": {
            "file_patterns": [
                r"Dockerfile",
                r"\.dockerfile$",
                r"docker-compose\.ya?ml$",
            ],
            "content_patterns": [
                r"FROM\s+\w+",
                r"RUN\s+.*",
                r"CMD\s+.*",
                r"ENTRYPOINT\s+.*",
            ],
            "version_files": [],
        },
        "shell": {
            "file_patterns": [r"\.sh$", r"\.bash$", r"\.zsh$"],
            "content_patterns": [
                r"#!/bin/(ba)?sh",
                r"if\s+\[\[.*\]\]",
                r"while\s+.*;\s*do",
            ],
            "version_files": [],
        },
        "html": {
            "file_patterns": [r"\.html$", r"\.htm$", r"\.xhtml$"],
            "content_patterns": [
                r"<!DOCTYPE\s+html>",
                r"<html.*?>",
                r"<head.*?>",
                r"<body.*?>",
            ],
            "version_files": [],
        },
        "css": {
            "file_patterns": [r"\.css$", r"\.scss$", r"\.sass$", r"\.less$"],
            "content_patterns": [r"@media", r"@import", r"\{[^}]*\}", r":\s*[^{};]+;"],
            "version_files": [],
        },
        "yaml": {
            "file_patterns": [r"\.ya?ml$"],
            "content_patterns": [],
            "version_files": [],
        },
        "json": {
            "file_patterns": [r"\.json$"],
            "content_patterns": [],
            "version_files": [],
        },
        "markdown": {
            "file_patterns": [r"\.md$", r"\.markdown$"],
            "content_patterns": [],
            "version_files": [],
        },
        "go": {
            "file_patterns": [r"\.go$", r"go\.mod$", r"go\.sum$"],
            "content_patterns": [
                r"package\s+\w+",
                r"import\s+\(",
                r"func\s+\w+\s*\(",
                r"type\s+\w+\s+struct\s*\{",
            ],
            "version_files": ["go.mod"],
        },
        "rust": {
            "file_patterns": [r"\.rs$", r"Cargo\.toml$", r"Cargo\.lock$"],
            "content_patterns": [
                r"fn\s+\w+\s*\(",
                r"struct\s+\w+",
                r"impl\s+\w+",
                r"mod\s+\w+",
                r"use\s+\w+",
            ],
            "version_files": ["Cargo.toml"],
        },
    }

    # Configuration parameters that could be made configurable
    HIDDEN_DIR_PATTERNS = [
        r"^\.git$",
        r"^\.svn$",
        r"^\.hg$",
        r"^__pycache__$",
        r"^\.venv$",
        r"^node_modules$",
        r"^\.pytest_cache$",
    ]
    MAX_FILES_TO_SCAN = 5000
    MAX_FILE_SIZE = 10000  # bytes

    def __init__(self, repo_path: str | None = None) -> None:
        """Initialize the file scanner.

        Args:
            repo_path: Path to repository to scan. If provided, scanning will be
                called automatically.
        """
        self.file_counts: dict[str, int] = {}
        self.detected_files: dict[str, set[str]] = {}
        self.tech_versions: dict[str, str | None] = {}

        # Automatically scan if path provided (for test compatibility)
        if repo_path:
            self.repo_path = Path(repo_path).resolve()
            # Initial values for fields that will be populated during scanning
            for tech in self.TECH_PATTERNS:
                self.file_counts[tech] = 0
                self.detected_files[tech] = set()
                self.tech_versions[tech] = None

    def _is_hidden(self, path_part: str) -> bool:
        """Check if a path component matches hidden directory patterns."""
        return any(re.match(pattern, path_part) for pattern in self.HIDDEN_DIR_PATTERNS)

    def _detect_version_from_package_json(self, file_path: str) -> None:
        """Detect versions from package.json."""
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                dependencies = data.get("dependencies", {})
                dev_dependencies = data.get("devDependencies", {})

                # React detection
                if "react" in dependencies:
                    self.tech_versions["react"] = dependencies["react"]
                    self.tech_versions["javascript"] = "detected-via-package.json"

                # Vue detection
                if "vue" in dependencies:
                    self.tech_versions["vue"] = dependencies["vue"]
                    self.tech_versions["javascript"] = "detected-via-package.json"

                # TypeScript detection
                if "typescript" in dependencies or "typescript" in dev_dependencies:
                    ts_version = dependencies.get("typescript") or dev_dependencies.get(
                        "typescript"
                    )
                    self.tech_versions["typescript"] = ts_version

                # Svelte detection
                if "svelte" in dependencies or "svelte" in dev_dependencies:
                    svelte_version = dependencies.get("svelte") or dev_dependencies.get(
                        "svelte"
                    )
                    self.tech_versions["svelte"] = svelte_version

        except (json.JSONDecodeError, OSError):
            pass  # Ignore errors in package.json parsing

    def _detect_version_from_pyproject_toml(self, file_path: str) -> None:
        """Detect versions from pyproject.toml.

        This is a simplified version that looks for Python version in
        requires-python field.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                # Look for requires-python = "<version spec>"
                match = re.search(r'requires-python\s*=\s*"([^"]+)"', content)
                if match:
                    self.tech_versions["python"] = match.group(1)
                # Very simple check for poetry
                elif "tool.poetry" in content:
                    self.tech_versions["python"] = "detected-via-poetry"
        except OSError:
            pass  # Ignore errors in pyproject.toml parsing

    def _detect_version_from_requirements_txt(self, file_path: str) -> None:
        """Detect versions from requirements.txt.

        This is a simplified version that just marks Python as detected.
        """
        try:
            # Just mark as detected, not trying to parse a specific version
            self.tech_versions["python"] = "detected-via-requirements"
        except OSError:
            pass  # Ignore errors in requirements.txt parsing

    def _detect_version_from_go_mod(self, file_path: str) -> None:
        """Detect versions from go.mod."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                # Extract Go version
                match = re.search(r"go (\d+\.\d+(?:\.\d+)?)", content)
                if match:
                    self.tech_versions["go"] = match.group(1)
        except OSError:
            pass  # Ignore errors in go.mod parsing

    def _detect_version_from_cargo_toml(self, file_path: str) -> None:
        """Detect versions from Cargo.toml."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                # Very simple check for Rust package
                if "[package]" in content:
                    self.tech_versions["rust"] = "detected-via-cargo"
        except OSError:
            pass  # Ignore errors in Cargo.toml parsing

    def _detect_version(self, tech: str, file_path: str) -> None:
        """Detect version for a technology from a given file."""
        file_name = os.path.basename(file_path)

        if file_name == "package.json":
            self._detect_version_from_package_json(file_path)
        elif file_name == "pyproject.toml":
            self._detect_version_from_pyproject_toml(file_path)
        elif file_name == "requirements.txt":
            self._detect_version_from_requirements_txt(file_path)
        elif file_name == "go.mod":
            self._detect_version_from_go_mod(file_path)
        elif file_name == "Cargo.toml":
            self._detect_version_from_cargo_toml(file_path)

    def _calculate_confidence(self, tech: str, count: int) -> float:
        """Calculate a confidence score for a technology.

        The score is based on the number of files found and any available version
        information.

        Args:
            tech: The technology to calculate confidence for
            count: Number of detected files

        Returns:
            A confidence score between 0.0 and 1.0
        """
        if count == 0:
            return 0.0

        # Base confidence from count
        if count >= 10:
            confidence = 0.9
        elif count >= 5:
            confidence = 0.7
        elif count >= 2:
            confidence = 0.5
        else:
            confidence = 0.3

        # Boost confidence if we have version info
        if self.tech_versions.get(tech) is not None:
            confidence = min(1.0, confidence + 0.1)

        # Adjust confidence for some special cases
        if tech == "python" and "requirements.txt" in self.detected_files.get(
            "python", set()
        ):
            confidence = min(1.0, confidence + 0.1)

        if tech == "javascript" and "package.json" in self.detected_files.get(
            "javascript", set()
        ):
            confidence = min(1.0, confidence + 0.1)

        return confidence

    def _read_file_content(self, file_path: str, max_size: int = MAX_FILE_SIZE) -> str:
        """Read first part of a file to identify content patterns.

        Args:
            file_path: Path to file
            max_size: Maximum number of bytes to read (default: 10000)

        Returns:
            String content of the file (may be partial)
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(max_size)
        except (UnicodeDecodeError, OSError, PermissionError):
            return ""

    def scan_repository(self, path: str) -> dict[str, TechInfo]:
        """Scan a repository to detect technologies based on file types.

        Args:
            path: The repository path to scan

        Returns:
            Dictionary mapping technology names to TechInfo objects
        """
        self.repo_path = Path(path).resolve()

        # Reset counters before starting
        self.file_counts = {tech: 0 for tech in self.TECH_PATTERNS}
        self.detected_files = {tech: set() for tech in self.TECH_PATTERNS}
        self.tech_versions = {tech: None for tech in self.TECH_PATTERNS}

        files_scanned = 0

        try:
            for root, dirs, files in os.walk(path, topdown=True):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not self._is_hidden(d)]

                for file in files:
                    # Check if we've hit the scan limit
                    if files_scanned >= self.MAX_FILES_TO_SCAN:
                        break

                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, path)

                    # Skip overly large files
                    try:
                        file_size = os.path.getsize(file_path)
                        if file_size > self.MAX_FILE_SIZE:
                            continue
                    except OSError:
                        continue  # Skip files with issues

                    # Check file name against patterns
                    file_matched = False
                    for tech, patterns in self.TECH_PATTERNS.items():
                        # Check file patterns
                        for pattern in patterns["file_patterns"]:
                            if re.search(pattern, file, re.IGNORECASE):
                                self.file_counts[tech] += 1
                                self.detected_files[tech].add(rel_path)
                                file_matched = True

                                # Check for version files
                                if file in patterns["version_files"]:
                                    self._detect_version(tech, file_path)
                                break

                    # If file already matched by name, skip content check
                    if file_matched:
                        files_scanned += 1
                        continue

                    # For unmatched files, check content patterns
                    try:
                        content = self._read_file_content(file_path)

                        for tech, patterns in self.TECH_PATTERNS.items():
                            if any(
                                re.search(pattern, content, re.MULTILINE)
                                for pattern in patterns["content_patterns"]
                            ):
                                self.file_counts[tech] += 1
                                self.detected_files[tech].add(rel_path)

                                # Check for version files (though less likely to match here)
                                if file in patterns["version_files"]:
                                    self._detect_version(tech, file_path)
                                break
                    except Exception:
                        pass  # Ignore errors in file content checking

                    files_scanned += 1

                # Break if we hit the scan limit
                if files_scanned >= self.MAX_FILES_TO_SCAN:
                    break

        except (PermissionError, OSError):
            # Handle permission errors gracefully
            pass

        # Calculate the technology info with confidence scores
        results = {}

        # Process the automatically implied technologies
        # We need to do this before calculating confidence
        implied_techs = self._get_implied_technologies()
        for tech, implied_by in implied_techs.items():
            # Update the count for tech if it was implied but not directly detected
            if tech not in self.file_counts or self.file_counts[tech] == 0:
                for implying_tech in implied_by:
                    if (
                        implying_tech in self.file_counts
                        and self.file_counts[implying_tech] > 0
                    ):
                        self.file_counts[tech] = max(1, self.file_counts.get(tech, 0))
                        # Version info could be carried over in some cases
                        if self.tech_versions.get(tech) is None:
                            self.tech_versions[tech] = f"implied-by-{implying_tech}"
                        break

        # Generate final results with confidence scores
        for tech, count in self.file_counts.items():
            if count > 0:
                confidence = self._calculate_confidence(tech, count)
                results[tech] = TechInfo(
                    name=tech,
                    count=count,
                    version=self.tech_versions.get(tech),
                    confidence=confidence,
                )

        return results

    def _get_implied_technologies(self) -> dict[str, list[str]]:
        """Get technologies that imply the presence of others.

        Returns:
            Dictionary mapping technology names to lists of technologies that imply them
        """
        return {
            "javascript": ["typescript", "react", "vue", "svelte"],
            "html": ["react", "vue", "svelte"],
            "css": ["react", "vue", "svelte"],
        }

    def detect_technologies(self) -> dict[str, TechInfo]:
        """Detect technologies in the already scanned repository.

        Returns:
            Dictionary mapping technology names to TechInfo objects
        """
        if not hasattr(self, "repo_path"):
            raise ValueError("Repository path not set. Call scan_repository first.")

        return self.scan_repository(str(self.repo_path))

    def get_detected_markers(self) -> dict[str, set[str]]:
        """Get a mapping of technologies to the files that marked detection.

        This is useful for debugging and understanding why a technology was detected.

        Returns:
            Dictionary mapping technology names to sets of file paths
        """
        return self.detected_files

    def _has_file_with_name(self, name: str) -> bool:
        """Check if any technology has a file with the given name.

        Args:
            name: Filename to check

        Returns:
            True if any technology has a file with this name
        """
        for tech, files in self.detected_files.items():
            if any(os.path.basename(file) == name for file in files):
                return True
        return False

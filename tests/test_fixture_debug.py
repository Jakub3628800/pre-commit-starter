"""Debug test for fixtures."""
import glob
import os
import re
import tempfile
from pathlib import Path

import pytest

from src.file_scanner import FileScanner


def test_frontend_repo_contents(sample_frontend_repo):
    """Test that the frontend repo fixture is correctly created."""
    # Print the directory contents
    files = list(sample_frontend_repo.glob("**/*"))
    print(f"\nFiles found in {sample_frontend_repo}:")
    for file in files:
        if file.is_file():
            print(f"  - {file.relative_to(sample_frontend_repo)}")

    # Check specific expected files
    assert (sample_frontend_repo / "package.json").exists()
    assert (sample_frontend_repo / "tsconfig.json").exists()
    assert (sample_frontend_repo / "src" / "components" / "App.tsx").exists()
    assert (sample_frontend_repo / "src" / "styles" / "App.css").exists()
    assert (sample_frontend_repo / "public" / "index.html").exists()

    # Inspect the scanner patterns directly
    scanner = FileScanner()

    # Check Python content patterns
    python_content_patterns = scanner.TECH_PATTERNS["python"]["content_patterns"]
    print("\nPython content patterns:")
    for pattern in python_content_patterns:
        print(f"  - {pattern}")

    # Read the App.tsx file content
    app_tsx_path = sample_frontend_repo / "src" / "components" / "App.tsx"
    app_tsx_content = app_tsx_path.read_text()
    print("\nApp.tsx content:")
    print(app_tsx_content)

    # Check if any Python patterns match the TypeScript file
    print("\nPython pattern matches in App.tsx:")
    for pattern in python_content_patterns:
        matches = re.findall(pattern, app_tsx_content)
        if matches:
            print(f"  Pattern '{pattern}' matched: {matches}")

    # Check detection
    detected = scanner.scan_repository(str(sample_frontend_repo))
    print(f"\nDetected technologies: {list(detected.keys())}")

    # Check markers
    markers = scanner.get_detected_markers()
    print("\nDetected file markers:")
    for tech, files in markers.items():
        print(f"  {tech}: {list(files)}")

    # Expected technologies
    assert "javascript" in detected
    assert "typescript" in detected
    assert "react" in detected
    assert "html" in detected
    assert "css" in detected

"""Tests for specific regex patterns in file_scanner.py."""

import re

from src.file_scanner import FileScanner


def test_python_import_patterns():
    """Test the regex patterns for Python imports."""
    # Get the patterns from FileScanner
    python_patterns = FileScanner.TECH_PATTERNS["python"]["content_patterns"]

    # Extract the specific patterns for imports
    import_pattern = python_patterns[0]  # 'import' pattern
    from_import_pattern = python_patterns[1]  # 'from ... import' pattern

    # Test valid Python imports
    valid_imports = [
        "import os",
        "import sys",
        "import numpy as np",
        "import pandas as pd",
        "import tensorflow",
        "import matplotlib.pyplot as plt",
    ]

    for valid_import in valid_imports:
        assert re.search(
            import_pattern, valid_import
        ), f"Failed to match valid import: {valid_import}"

    # Test valid Python from imports
    valid_from_imports = [
        "from os import path",
        "from sys import argv",
        "from numpy import array",
        "from pandas import DataFrame",
        "from tensorflow import keras",
        "from matplotlib.pyplot import plot",
        "from django.db.models import Q",
        "from mypackage.mymodule.mysubmodule import MyClass",
    ]

    for valid_from_import in valid_from_imports:
        assert re.search(
            from_import_pattern, valid_from_import
        ), f"Failed to match valid from import: {valid_from_import}"

    # Test imports with comments before them (should not match)
    commented_imports = [
        "# import os",
        "// import sys",
        "/* import numpy */",
        "# from os import path",
        "// from sys import argv",
    ]

    for commented_import in commented_imports:
        if commented_import.startswith("#"):
            # Python comments should not match
            assert not re.search(
                import_pattern, commented_import
            ), f"Incorrectly matched commented import: {commented_import}"
            assert not re.search(
                from_import_pattern, commented_import
            ), f"Incorrectly matched commented import: {commented_import}"


def test_shell_script_detection():
    """Test the regex patterns for shell scripts."""
    # Get the patterns from FileScanner
    shell_patterns = FileScanner.TECH_PATTERNS["shell"]["content_patterns"]

    # Valid shell script content
    valid_shell_content = [
        "#!/bin/bash\necho 'hello'",
        "#!/bin/sh\nif [ -f file.txt ]; then echo 'exists'; fi",
        "if [[ $var == 'test' ]]; then echo 'yes'; fi",
        "while read line; do echo $line; done",
    ]

    for content in valid_shell_content:
        matched = False
        for pattern in shell_patterns:
            if re.search(pattern, content):
                matched = True
                break
        assert matched, f"Failed to match valid shell content: {content}"

"""Validate that non-exported functions are not imported from outside the library."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from pre_commit_tools.check_exports.export_parser import get_exported_functions, get_init_path, get_library_root
from pre_commit_tools.check_exports.import_detector import find_imports_via_ast
from pre_commit_tools.check_exports.exceptions import NoInitFileError, InvalidLibraryPath


class Violation:
    """Represents an import violation.

    Attributes:
        lib_name: Name of the library where violation occurred
        func_name: Name of the non-exported function that was imported
        file_path: Path to the file with the violating import
        line_num: Line number in the file where the violation occurred
    """

    def __init__(self, lib_name: str, func_name: str, file_path: str, line_num: int) -> None:
        """Initialize a violation.

        Args:
            lib_name: Name of the library being imported from
            func_name: Name of the non-exported function
            file_path: Path to file containing the import
            line_num: Line number of the import statement
        """
        self.lib_name = lib_name
        self.func_name = func_name
        self.file_path = file_path
        self.line_num = line_num

    def __repr__(self) -> str:
        return (
            f"{self.file_path}:{self.line_num}: Function '{self.func_name}' "
            f"is not exported from '{self.lib_name}'\n"
            f"              → Add '{self.func_name}' to {self.lib_name}.__init__.py "
            f"or use internal imports only"
        )


def validate_library(
    lib_path: str,
    exclude_patterns: Optional[List[str]] = None,
    verbose: bool = False,
) -> tuple[List[Violation], Dict[str, Any]]:
    """
    Validate that no non-exported functions are imported from outside the library.

    Args:
        lib_path: Path to library to check
        exclude_patterns: List of patterns to exclude from checking
        verbose: Whether to return statistics

    Returns:
        Tuple of (violations list, statistics dict)
    """
    import fnmatch
    import time

    start_time = time.time()
    exclude_patterns = exclude_patterns or []

    lib_root = get_library_root(lib_path)
    lib_name = lib_root.name

    # Get all exported functions
    init_path = get_init_path(lib_root)
    exported = get_exported_functions(init_path)

    # Find all imports
    imports = find_imports_via_ast(lib_root)

    violations: List[Violation] = []

    for import_key, locations in imports.items():
        # import_key is "lib_name.func_name"
        parts = import_key.split(".", 1)
        if len(parts) != 2:
            continue

        lib, func_name = parts

        # Only process imports from this specific library
        if lib != lib_name:
            continue

        # Check if function is exported
        if func_name not in exported:
            # Check if import is from within the library (internal import is OK)
            for file_path, line_num in locations:
                file_p = Path(file_path)

                # Check if file matches exclude patterns
                should_exclude = False
                for pattern in exclude_patterns:
                    if fnmatch.fnmatch(str(file_p), pattern):
                        should_exclude = True
                        break

                if should_exclude:
                    continue

                # If the importing file is inside the library, it's an internal import (allowed)
                if not file_p.is_relative_to(lib_root):
                    violations.append(Violation(lib_name, func_name, str(file_path), line_num))

    # Calculate statistics
    stats = {
        "lib_name": lib_name,
        "exports_count": len(exported),
        "imports_count": len(imports),
        "violations_count": len(violations),
        "execution_time": time.time() - start_time,
    }

    return violations, stats


def validate_libraries(
    lib_paths: List[str],
    exclude_patterns: Optional[List[str]] = None,
    verbose: bool = False,
) -> tuple[List[Violation], Dict[str, Any]]:
    """
    Validate multiple libraries.

    Args:
        lib_paths: List of library paths to check
        exclude_patterns: List of patterns to exclude from checking
        verbose: Whether to return statistics

    Returns:
        Tuple of (combined violations list, statistics dict)
    """
    all_violations: List[Violation] = []
    all_stats = {
        "libraries": [],
        "total_exports": 0,
        "total_imports": 0,
        "total_violations": 0,
        "total_execution_time": 0.0,
    }

    for lib_path in lib_paths:
        violations, stats = validate_library(lib_path, exclude_patterns, verbose)
        all_violations.extend(violations)

        all_stats["libraries"].append(stats)
        all_stats["total_exports"] += stats["exports_count"]
        all_stats["total_imports"] += stats["imports_count"]
        all_stats["total_violations"] += stats["violations_count"]
        all_stats["total_execution_time"] += stats["execution_time"]

    return all_violations, all_stats

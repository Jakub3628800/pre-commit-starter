"""Validate that non-exported functions are not imported from outside the library."""

from pathlib import Path
from typing import List, Optional, Tuple, TypedDict

from pre_commit_tools.check_exports.export_parser import (
    get_exported_functions,
    get_init_path,
    get_library_root,
)
from pre_commit_tools.check_exports.import_detector import find_imports_via_ast


class SingleLibraryStats(TypedDict):
    """Type definition for statistics from a single library validation."""

    lib_name: str
    exports_count: int
    imports_count: int
    violations_count: int
    execution_time: float


class AggregatedStats(TypedDict):
    """Type definition for aggregated statistics from multiple library validations."""

    libraries: List[SingleLibraryStats]
    total_exports: int
    total_imports: int
    total_violations: int
    total_execution_time: float


class Violation:
    """Represents an import violation.

    Attributes:
        lib_name: Name of the library where violation occurred
        func_name: Name of the non-exported function that was imported
        file_path: Path to the file with the violating import
        line_num: Line number in the file where the violation occurred
        is_warning: If True, this is a warning (e.g. underscore export) rather than an error
        hint: Optional suggestion for fixing the violation
    """

    def __init__(
        self,
        lib_name: str,
        func_name: str,
        file_path: str,
        line_num: int,
        is_warning: bool = False,
        hint: Optional[str] = None,
    ) -> None:
        """Initialize a violation.

        Args:
            lib_name: Name of the library being imported from
            func_name: Name of the non-exported function
            file_path: Path to file containing the import
            line_num: Line number of the import statement
            is_warning: If True, this is a warning
            hint: Optional suggestion
        """
        self.lib_name = lib_name
        self.func_name = func_name
        self.file_path = file_path
        self.line_num = line_num
        self.is_warning = is_warning
        self.hint = hint

    def __repr__(self) -> str:
        prefix = "WARN" if self.is_warning else "ERR"
        msg = (
            f"[{prefix}] {self.file_path}:{self.line_num}: Function '{self.func_name}' "
            f"is not exported from '{self.lib_name}'"
        )
        if self.is_warning:
            msg = (
                f"[{prefix}] {self.file_path}:{self.line_num}: Symbol '{self.func_name}' "
                f"is exported from '{self.lib_name}' but starts with underscore"
            )

        if self.hint:
            msg += f"\n              → {self.hint}"
        elif not self.is_warning:
            msg += f"\n              → Add '{self.func_name}' to {self.lib_name}.__init__.py or use internal imports only"
        return msg


def validate_library(
    lib_path: str,
    exclude_patterns: Optional[List[str]] = None,
    public_submodules: Optional[List[str]] = None,
    verbose: bool = False,
) -> Tuple[List[Violation], SingleLibraryStats]:
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
    public_submodules_set = set(public_submodules or [])

    lib_root = get_library_root(lib_path)
    lib_name = lib_root.name

    # Get all exported functions
    init_path = get_init_path(lib_root)
    exported = get_exported_functions(init_path)

    # Find all imports
    imports = find_imports_via_ast(lib_root)

    violations: List[Violation] = []

    # Check for underscore exports (Warnings)
    for func in exported:
        if func.startswith("_"):
            # We don't have a specific file/line for the export definition easily available
            # so we'll just report it as a general warning for the library init
            violations.append(
                Violation(
                    lib_name,
                    func,
                    str(init_path),
                    1,
                    is_warning=True,
                    hint="Symbols starting with underscore should not be exported in __init__.py",
                )
            )

    for import_key, locations in imports.items():
        # import_key can be:
        # - "mylib.foo" (direct import from mylib)
        # - "mylib.sub.foo" (import from submodule)

        # Check if this import is from our library
        if not import_key.startswith(lib_name + "."):
            continue

        # Extract the path relative to lib_name
        # e.g. "mylib.foo" -> "foo"
        # e.g. "mylib.sub.foo" -> "sub.foo"
        relative_path = import_key[len(lib_name) + 1 :]

        # Check if this is directly exported
        if relative_path in exported:
            continue

        # Check if it's a public submodule import
        # e.g. relative_path="sub.foo", public_submodules=["sub"]
        is_public_submodule = False
        for submod in public_submodules_set:
            if relative_path == submod or relative_path.startswith(submod + "."):
                is_public_submodule = True
                break

        if is_public_submodule:
            continue

        # If we get here, it's a violation
        # Check each location to see if it's external
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
                # Generate hint
                hint = None
                if "." in relative_path:
                    # It's from a submodule
                    parts = relative_path.split(".")
                    if len(parts) == 2:
                        submod_name, func = parts
                        hint = f"Found in '{lib_name}.{submod_name}'. Add '{submod_name}' to public_submodules or export '{func}' in __init__.py"
                    else:
                        # Deeper nesting
                        hint = f"Consider adding '{parts[0]}' to public_submodules or restructuring exports"

                violations.append(
                    Violation(
                        lib_name, relative_path, str(file_path), line_num, hint=hint
                    )
                )

    # Calculate statistics
    stats: SingleLibraryStats = {
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
    public_submodules: Optional[List[str]] = None,
    verbose: bool = False,
) -> Tuple[List[Violation], AggregatedStats]:
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
    all_stats: AggregatedStats = {
        "libraries": [],
        "total_exports": 0,
        "total_imports": 0,
        "total_violations": 0,
        "total_execution_time": 0.0,
    }

    for lib_path in lib_paths:
        violations, stats = validate_library(
            lib_path, exclude_patterns, public_submodules, verbose
        )
        all_violations.extend(violations)

        all_stats["libraries"].append(stats)
        all_stats["total_exports"] += stats["exports_count"]
        all_stats["total_imports"] += stats["imports_count"]
        all_stats["total_violations"] += stats["violations_count"]
        all_stats["total_execution_time"] += stats["execution_time"]

    return all_violations, all_stats

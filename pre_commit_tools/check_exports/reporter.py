"""Report violations in a human-readable format."""

import json
from typing import List

from pre_commit_tools.check_exports.validator import Violation

# ANSI color codes
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Global flag for color support
_use_colors = True


def set_use_colors(use_colors: bool) -> None:
    """Set whether to use colored output."""
    global _use_colors
    _use_colors = use_colors


def _colorize(text: str, color: str) -> str:
    """Apply color to text if colors are enabled."""
    if not _use_colors:
        return text
    return f"{color}{text}{RESET}"


def report_violations(
    violations: List[Violation], format: str = "text", use_colors: bool = True
) -> None:
    """
    Print violations to stdout in a readable format.

    Args:
        violations: List of violations to report
        format: Output format - 'text' or 'json'
        use_colors: Whether to use colored output
    """
    set_use_colors(use_colors)

    if format == "json":
        report_violations_json(violations)
    else:
        report_violations_text(violations)


def report_violations_text(violations: List[Violation]) -> None:
    """Print violations in human-readable text format with colors."""
    header = f"✗ Found {len(violations)} export violation(s):"
    print(f"\n{_colorize(header, RED + BOLD)}\n", flush=True)

    # Group violations by library
    by_lib: dict[str, List[Violation]] = {}
    for violation in violations:
        if violation.lib_name not in by_lib:
            by_lib[violation.lib_name] = []
        by_lib[violation.lib_name].append(violation)

    # Print grouped by library
    for lib_name in sorted(by_lib.keys()):
        lib_violations = by_lib[lib_name]
        lib_header = f"Library: {lib_name}"
        print(f"  {_colorize(lib_header, BOLD + YELLOW)}")

        for violation in lib_violations:
            print(f"    {_colorize(str(violation), RED)}")

        print()


def report_violations_json(violations: List[Violation]) -> None:
    """Print violations in JSON format for tool integration."""
    violations_list = [
        {
            "lib_name": v.lib_name,
            "func_name": v.func_name,
            "file_path": v.file_path,
            "line_num": v.line_num,
        }
        for v in violations
    ]

    output = {
        "status": "violations_found",
        "count": len(violations),
        "violations": violations_list,
    }

    print(json.dumps(output, indent=2))


def report_success(
    message: str = "✓ All libraries passed export validation",
    format: str = "text",
    use_colors: bool = True,
) -> None:
    """Print success message."""
    set_use_colors(use_colors)

    if format == "json":
        print(json.dumps({"status": "ok", "message": message}))
    else:
        print(_colorize(message, GREEN))


def report_summary(
    total_files: int,
    total_exports: int,
    violations_count: int,
    execution_time: float = 0.0,
    format: str = "text",
    use_colors: bool = True,
) -> None:
    """Print summary statistics."""
    set_use_colors(use_colors)

    if format == "json":
        summary = {
            "status": "summary",
            "total_files": total_files,
            "total_exports": total_exports,
            "violations": violations_count,
            "execution_time_ms": round(execution_time * 1000, 2),
        }
        print(json.dumps(summary))
    else:
        summary_text = (
            f"\n{_colorize('Summary:', BOLD)}\n"
            f"  Files checked: {total_files}\n"
            f"  Exports found: {total_exports}\n"
            f"  Violations: {violations_count}\n"
        )
        if execution_time > 0:
            summary_text += f"  Time: {execution_time * 1000:.2f}ms\n"
        print(summary_text)

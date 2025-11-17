"""Parse library __init__.py to extract exported functions."""

import ast
from pathlib import Path
from typing import Set


def get_exported_functions(init_path: Path) -> Set[str]:
    """
    Extract all functions exported from a library's __init__.py.

    Functions are considered exported if they are:
    1. Directly defined in __init__.py
    2. Imported explicitly (including __all__ list)

    Args:
        init_path: Path to __init__.py file

    Returns:
        Set of exported function names
    """
    if not init_path.exists():
        return set()

    try:
        tree = ast.parse(init_path.read_text())
    except SyntaxError:
        return set()

    exported = set()

    # Check for __all__ definition
    all_list = _get_all_list(tree)
    if all_list:
        exported.update(all_list)

    # Find all function definitions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            exported.add(node.name)
        elif isinstance(node, ast.ImportFrom):
            # Handle "from X import Y" statements
            for alias in node.names:
                if alias.name != "*":
                    exported.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            # Handle "import X" or "import X as Y"
            for alias in node.names:
                exported.add(alias.asname or alias.name)

    return exported


def _get_all_list(tree: ast.Module) -> Set[str]:
    """Extract __all__ list from module if it exists."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    return {
                        elt.value
                        for elt in node.value.elts
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                    }
    return set()


def get_library_root(lib_path: str) -> Path:
    """
    Convert library path to absolute Path object.

    Args:
        lib_path: Path to library (can be relative or absolute)

    Returns:
        Absolute Path to library
    """
    return Path(lib_path).resolve()


def get_init_path(lib_root: Path) -> Path:
    """Get path to __init__.py for a library."""
    return lib_root / "__init__.py"

"""Detect function imports via AST parsing."""

from pathlib import Path
from typing import Dict, List, Tuple


def find_imports_via_ast(lib_root: Path) -> Dict[str, List[Tuple[str, int]]]:
    """
    Find function imports by parsing all Python files in the codebase.

    Args:
        lib_root: Path to library being checked

    Returns:
        Dict mapping (lib_name, function_name) to list of file:line locations
    """
    import ast

    lib_name = lib_root.name
    codebase_root = lib_root.parent
    imports: Dict[str, List[Tuple[str, int]]] = {}

    # Walk all Python files in codebase
    for py_file in codebase_root.rglob("*.py"):
        # Skip the library itself - we only care about external imports
        if py_file.is_relative_to(lib_root):
            continue

        try:
            tree = ast.parse(py_file.read_text())
        except (SyntaxError, UnicodeDecodeError):
            continue

        # Find all imports from our target library
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                # Check if import is from our library
                if node.module and node.module.startswith(lib_name):
                    for alias in node.names:
                        func_name = alias.name
                        # Skip star imports (*) - they respect __all__ automatically
                        if func_name == "*":
                            continue
                        key = f"{lib_name}.{func_name}"
                        if key not in imports:
                            imports[key] = []
                        imports[key].append((str(py_file), node.lineno))
            elif isinstance(node, ast.Import):
                # Handle direct imports like "import lib.module.function"
                for alias in node.names:
                    if alias.name.startswith(lib_name):
                        func_name = alias.name.split(".")[-1]
                        key = f"{lib_name}.{func_name}"
                        if key not in imports:
                            imports[key] = []
                        imports[key].append((str(py_file), node.lineno))

    return imports

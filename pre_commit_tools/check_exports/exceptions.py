"""Custom exceptions for check-exports."""


class CheckExportsError(Exception):
    """Base exception for all check-exports errors."""

    pass


class LibraryNotFoundError(CheckExportsError):
    """Raised when a library path cannot be found."""

    def __init__(self, lib_path: str):
        self.lib_path = lib_path
        super().__init__(f"Library not found: {lib_path}")


class NoInitFileError(CheckExportsError):
    """Raised when __init__.py is missing from a library."""

    def __init__(self, lib_path: str):
        self.lib_path = lib_path
        super().__init__(f"No __init__.py found in library: {lib_path}")


class SyntaxErrorInFile(CheckExportsError):
    """Raised when a Python file has a syntax error."""

    def __init__(self, file_path: str, error_msg: str):
        self.file_path = file_path
        self.error_msg = error_msg
        super().__init__(f"Syntax error in {file_path}: {error_msg}")


class InvalidLibraryPath(CheckExportsError):
    """Raised when the provided path is not a valid library."""

    def __init__(self, lib_path: str):
        self.lib_path = lib_path
        super().__init__(f"Invalid library path: {lib_path}")

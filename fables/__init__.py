"""
Define functions, classes, and constants that are exposed to the client,
enabling calls to fables.* .
"""

from fables.api import detect, parse
from fables.tree import (
    StreamManager,
    FileNode,
    MimeTypeFileNode,
    Directory,
    Zip,
    Csv,
    Xls,
    Xlsx,
    Skip,
    mimetype_from_stream,
    mimetype_and_extension,
)
from fables.table import Table
from fables.errors import ParseError, ExtractError
from fables.constants import OS_PATTERNS_TO_SKIP, MAX_FILE_SIZE

__all__ = [
    "detect",
    "parse",
    "StreamManager",
    "FileNode",
    "MimeTypeFileNode",
    "Directory",
    "Zip",
    "Csv",
    "Xls",
    "Xlsx",
    "Skip",
    "mimetype_from_stream",
    "mimetype_and_extension",
    "Table",
    "ParseError",
    "ExtractError",
    "OS_PATTERNS_TO_SKIP",
    "MAX_FILE_SIZE",
]

# Note: When changing version also be sure to change the version in setup.py
__version__ = "1.1.0"

"""
Define errors that fables catches.

A `ParseError` is a bundled object returned from visiting a node that is
parsed for tabular data, and some error occured.

An `ExtractError` is a bundled object returned from yielding a nodes
children from an archive file. This could happen when the archive is
password protected, but a password is not supplied by the user.
"""

from dataclasses import dataclass
from typing import Optional, Type


@dataclass
class Error:
    message: str
    exception_type: Type[Exception]
    name: Optional[str] = None
    sheet: Optional[str] = None


@dataclass
class ParseError(Error):
    pass


@dataclass
class ExtractError(Error):
    pass

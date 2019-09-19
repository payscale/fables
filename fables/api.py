"""
Implements the two main function entry points for fables:
`parse()` and `detect()`.
"""

import os
from io import BufferedIOBase
from typing import Any, Dict, IO, Iterable, Optional, Tuple, Union

from fables.constants import MAX_FILE_SIZE
from fables.parse import ParseVisitor
from fables.results import ParseResult
from fables.tree import FileNode, node_from_file


def _check_file_size(name: str) -> Tuple[bool, int]:
    file_size = os.stat(name).st_size
    return file_size > MAX_FILE_SIZE, file_size


def _check_stream_size(stream: IO[bytes]) -> Tuple[bool, int]:
    stream.seek(0, 2)
    stream_size = stream.tell()
    stream.seek(0)
    return stream_size > MAX_FILE_SIZE, stream_size


def _parse_user_input(
    io: Union[str, IO[bytes], None],
    calling_func_name: str,
    password: Optional[str] = None,
    passwords: Optional[Dict[str, str]] = {},
    stream_file_name: Optional[str] = None,
) -> Tuple[Optional[str], Optional[IO[bytes]], Dict[str, str]]:
    if isinstance(io, str):
        stream = None
        name = io
        if not os.path.exists(io):
            raise ValueError(
                f"str argument io for '{calling_func_name}' must exist on disk"
            )
        size_is_too_big, size = _check_file_size(name)
    else:
        if not isinstance(io, BufferedIOBase):
            raise TypeError(
                f"Argument io for '{calling_func_name}' must be instance of "
                + "str or a subclass of 'io.BufferedIOBase'"
            )
        stream = io
        name = getattr(stream, "name", stream_file_name)
        size_is_too_big, size = _check_stream_size(stream)

    if size_is_too_big:
        raise ValueError(
            f"In '{calling_func_name}', argument '{name}' has "
            + f"size={size} > fables.MAX_FILE_SIZE = "
            + f"{MAX_FILE_SIZE} bytes"
        )

    if passwords is not None and not isinstance(passwords, dict):
        raise ValueError(
            f"Argument 'passwords' in {calling_func_name} must be of type dict"
        )

    if password is not None and not isinstance(password, str):
        raise ValueError(
            f"Argument 'password' in {calling_func_name} must be of type str"
        )

    if passwords is None:
        passwords = {}

    if name is not None and password is not None:
        passwords[name] = password

    return name, stream, passwords


def detect(
    io: Union[str, IO[bytes], None],
    *,
    calling_func_name: Optional[str] = None,
    password: Optional[str] = None,
    passwords: Optional[Dict[str, str]] = None,
    stream_file_name: Optional[str] = None,
) -> FileNode:
    if calling_func_name is None:
        calling_func_name = "detect"
    name, stream, passwords = _parse_user_input(
        io=io,
        calling_func_name=calling_func_name,
        password=password,
        passwords=passwords,
        stream_file_name=stream_file_name,
    )
    return node_from_file(name=name, stream=stream, passwords=passwords)


def parse(
    io: Union[str, IO[bytes], None] = None,
    *,
    tree: Optional[FileNode] = None,
    password: Optional[str] = None,
    passwords: Optional[Dict[str, str]] = None,
    stream_file_name: Optional[str] = None,
    force_numeric: bool = True,
    pandas_kwargs: Dict[str, Any] = {},
) -> Iterable[ParseResult]:
    if tree is None:
        if io is None:
            raise ValueError(
                "One of parse() argumentes 'io' or 'tree' must "
                + "be given a value that is not None"
            )
        tree = detect(
            io=io,
            calling_func_name="parse",
            password=password,
            passwords=passwords,
            stream_file_name=stream_file_name,
        )

    visitor = ParseVisitor(force_numeric=force_numeric, pandas_kwargs=pandas_kwargs)
    yield from visitor.visit(tree)

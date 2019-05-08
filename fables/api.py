"""
Implements the two main function entry points for fables:
`parse()` and `detect()`.
"""

import os
from io import BufferedIOBase
from typing import (
    Dict,
    IO,
    Iterable,
    Optional,
    Tuple,
    Union,
)

from fables.constants import MAX_FILE_SIZE
from fables.tree import FileNode, node_from_file
from fables.parse import ParseResult, ParseVisitor


def _check_file_size(name: str) -> Tuple[bool, int]:
    """Function that returns a tuple(boolean, int), where
    argument 1 (boolean) indicates if the filesize is larger than the MAX_FILE_SIZE,
    argument 2 (int) is the filesize (bytes) of an file-object, given a file-location string.

    Args:
        name (str): String which is the file-object location.

    Returns:
        (boolean, int): boolean- indicator if file-object is larger than MAX_FILE_SIZE,
            int- filesize in bytes.

    Note: functions and classes that start with an underscore are ignored in the Sphinx documentation.

    """
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
                f"Argument io for '{calling_func_name}' must be instance of " +
                "str or a subclass of 'io.BufferedIOBase'"
            )
        stream = io
        name = getattr(stream, 'name', stream_file_name)
        size_is_too_big, size = _check_stream_size(stream)

    if size_is_too_big:
        raise ValueError(
            f"In '{calling_func_name}', argument '{name}' has " +
            f'size={size} > fables.MAX_FILE_SIZE = ' +
            f'{MAX_FILE_SIZE} bytes'
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
    """Function description here.

    Args:
        io (typing.Union of str, io-bytes object, None): description
        * (additional arguments): description
        calling_func_name (string): description
        password (string): description
        passwords (dictionary): description
        stream_file_name (string): description

    Returns:
        Node-From-File object
    """
    if calling_func_name is None:
        calling_func_name = 'detect'
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
) -> Iterable[ParseResult]:
    """ Function Description here.

    Args:
        io typing.Union of (string, io-bytes object, None), Description
        * additional arguments
        tree (FileNode): Description
        password (string): Description
        passwords (dictionary): Description
        stream_file_name (string): Description

    Returns:
        Iterable
    """
    if tree is None:
        if io is None:
            raise ValueError(
                "One of parse() argumentes 'io' or 'tree' must " +
                "be given a value that is not None"
            )
        tree = detect(
            io=io,
            calling_func_name='parse',
            password=password,
            passwords=passwords,
            stream_file_name=stream_file_name,
        )

    visitor = ParseVisitor()
    yield from visitor.visit(tree)

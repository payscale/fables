"""
Define nodes of the detection tree. Nodes are responsible for how they
list their children, detecting if they are pw-protected, and in some
cases how they can be identified (e.g. by a heuristic on their mimetype
and extension)

Also implements the module-level function: `node_from_file()` which
determines what node to assign an input file.
"""

import io
import os
import zipfile
from fnmatch import fnmatch
from typing import Dict, IO, Iterator, List, Optional, Tuple

import magic
from msoffcrypto import OfficeFile  # type: ignore
from msoffcrypto.__main__ import is_encrypted

from fables.constants import OS_PATTERNS_TO_SKIP
from fables.errors import ExtractError


UNEXPECTED_DECRYPTION_EXCEPTION_MESSAGE = (
    "Unexpected exception occured when decrypting: {0}. Exception: {1}."
)


class IncorrectPassword(Exception):
    pass


class StreamManager:
    """If the user passes in a stream, just use that. Otherwise
    use a managed open file as a stream.

    This makes it so the user of the stream doesn't have to worry
    about closing it to save resources or keeping it open to not
    step on the user's open stream. It also keeps the interface
    the same, whether or not an open stream already exists.
    """

    def __init__(self, name: Optional[str], stream: Optional[IO[bytes]]) -> None:
        self.name = name
        self.stream = stream
        if self.stream is not None:
            self.stream.seek(0)
        self.opened_stream: Optional[IO[bytes]] = None

    def __enter__(self) -> IO[bytes]:
        if self.stream is not None:
            self.stream.seek(0)
            return self.stream

        if self.name is None:
            raise RuntimeError(
                "Cannot compute 'io.BufferedIOBase' for without "
                + "'name' or 'stream' property"
            )

        self.opened_stream = open(self.name, "rb")
        return self.opened_stream

    def __exit__(self, *exc) -> None:  # type: ignore
        if self.opened_stream is not None and hasattr(self.opened_stream, "close"):
            self.opened_stream.close()


class FileNode:
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        stream: Optional[IO[bytes]] = None,
        mimetype: Optional[str] = None,
        extension: Optional[str] = None,
        passwords: Dict[str, str] = {},
    ) -> None:
        self.name = name or getattr(stream, "name", None)
        self._stream = stream
        self.mimetype = mimetype
        self.extension = extension
        self.passwords = passwords

        self.extract_errors: List[ExtractError] = []

        self._decrypted_stream: Optional[IO[bytes]] = None

    @property
    def empty(self) -> bool:
        return self.mimetype == "application/x-empty"

    @property
    def stream(self) -> StreamManager:
        """Usage:
        >>> with node.stream as bytesio:
        >>>     bytes = bytesio.read()
        """
        return StreamManager(name=self.name, stream=self._stream)

    @property
    def children(self) -> Iterator["FileNode"]:
        yield from []

    @property
    def encrypted(self) -> bool:
        return False

    def add_password(self, name: str, password: str) -> None:
        self.passwords[name] = password

    @property
    def password(self) -> Optional[str]:
        """Assigns to this node property, the password that is key'd by the
        longest os-normalized sub-path of the node file name.

        E.g. for node.name == sub_dir_1/encrypted.xlsx, the following file-paths

            1. sub_dir_1/encrypted.xlsx
            2. encrypted.xlsx
            3. sub_dir_2/encrypted.xlsx

        are ordered by best key to use for the password.
        """
        if self.name is None:
            return None

        match_metrics: List[Tuple[bool, int, str]] = []
        for path, password in self.passwords.items():
            is_match = fnmatch(self.name, f"*{path}")
            match_metrics.append((is_match, len(path), password))

        if not match_metrics:
            return None

        # sort on match truthiness first then on file-path length
        return sorted(match_metrics, reverse=True)[0][-1]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, mimetype={self.mimetype})"


class MimeTypeFileNode(FileNode):
    MIMETYPES: List[str] = []
    EXTENSIONS: List[str] = []

    @classmethod
    def is_my_mimetype_or_extension(
        cls, mimetype: Optional[str], extension: Optional[str]
    ) -> bool:
        if mimetype is not None and mimetype in cls.MIMETYPES:
            if mimetype == cls.MIMETYPES[0]:
                return True
            elif extension is not None and extension.lower() in cls.EXTENSIONS:
                return True
        return False


class Zip(MimeTypeFileNode):
    MIMETYPES = ["application/zip"]
    EXTENSIONS = ["zip"]

    @property
    def _bytes_password(self) -> Optional[bytes]:
        str_password = self.password
        if str_password is not None:
            return str_password.encode("utf-8")
        return None

    @staticmethod
    def _encrypted_from_bit_signature(zf: zipfile.ZipFile) -> bool:
        """Stdlib impl here:
        https://github.com/python/cpython/blob/3.7/Lib/zipfile.py#L1514
        to understand why, search for "bit 0: If set" in:
        https://www.iana.org/assignments/media-types/application/zip
        basically we are checking if the 0th bit is 0 or 1
        """
        return bool(zf.infolist()[0].flag_bits & 0x1)

    def _password_decrypts(self) -> bool:
        if self.password is None:
            return False

        with self.stream as node_stream:
            with zipfile.ZipFile(node_stream) as zf:
                first_child_file = zf.namelist()[0]
                try:
                    zf.open(first_child_file, pwd=self._bytes_password)
                    return True
                except RuntimeError as e:
                    if "Bad password for file" in str(e):
                        return False
                    else:
                        raise RuntimeError(
                            UNEXPECTED_DECRYPTION_EXCEPTION_MESSAGE.format(
                                self.name, str(e)
                            )
                        )

    @property
    def encrypted(self) -> bool:
        with self.stream as node_stream:
            with zipfile.ZipFile(node_stream) as zf:
                if self._encrypted_from_bit_signature(zf):
                    return not self._password_decrypts()
        return False

    @property
    def children(self) -> Iterator[FileNode]:
        try:
            with self.stream as node_stream:
                with zipfile.ZipFile(node_stream) as zf:
                    for child_file in zf.namelist():
                        with zf.open(
                            child_file, pwd=self._bytes_password
                        ) as child_stream:
                            # TODO(Thomas: 3/5/2019):
                            #     Reading the zipfile bytes into a BytesIO stream
                            #     instead of using the default zipfile stream because
                            #     our usage of zipfile trips the cyclic redundancy
                            #     checks (bad CRC-32) of the zipfile.ZipExtFile.
                            #     Similar issue: https://stackoverflow.com/questions/5624669/strange-badzipfile-bad-crc-32-problem/5626098  # noqa: E501
                            #     I don't think passing this along to the BytesIO instance
                            #     is too expensive to worry about fixing this issue now.
                            bytes_stream = io.BytesIO(child_stream.read())
                            if self.name is not None:
                                child_file_path = os.path.join(
                                    os.path.basename(self.name), child_file
                                )
                                yield node_from_file(
                                    name=child_file_path,
                                    stream=bytes_stream,
                                    passwords=self.passwords,
                                )
                            else:
                                yield node_from_file(
                                    name=child_file,
                                    stream=bytes_stream,
                                    passwords=self.passwords,
                                )
        except RuntimeError as e:
            extract_error = ExtractError(
                message=str(e), exception_type=type(e), name=self.name
            )
            self.extract_errors.append(extract_error)


class ExcelEncryptionMixin(FileNode):
    def __init__(self, **kwargs) -> None:  # type: ignore
        super().__init__(**kwargs)
        self._raw_stream_mgr: StreamManager = super().stream
        self._decrypted_stream: Optional[IO[bytes]] = None

    @staticmethod
    def decrypt(encrypted_stream: IO[bytes], password: str) -> IO[bytes]:
        try:
            office_file = OfficeFile(encrypted_stream)
            decrypted_stream = io.BytesIO()
            office_file.load_key(password=password)
            office_file.decrypt(decrypted_stream)
            decrypted_stream.seek(0)
            return decrypted_stream
        except Exception as e:
            # xlsx exception message: 'The file could not be decrypted with this password'
            # xls exception message:  'Failed to verify password'
            if "password" in str(e):
                raise IncorrectPassword()
            else:
                raise RuntimeError(
                    UNEXPECTED_DECRYPTION_EXCEPTION_MESSAGE.format(
                        getattr(encrypted_stream, "name", None), str(e)
                    )
                )

    @property
    def encrypted(self) -> bool:
        with self._raw_stream_mgr as raw_stream:
            if is_encrypted(raw_stream):
                if self.password is not None:
                    try:  # to see if the password works
                        self._decrypted_stream = self.decrypt(raw_stream, self.password)
                        return False
                    except IncorrectPassword:
                        pass
                return True
        return False

    @property
    def stream(self) -> StreamManager:
        if not self.encrypted and self._decrypted_stream is not None:
            return StreamManager(self.name, self._decrypted_stream)
        else:
            return self._raw_stream_mgr


class Xlsx(MimeTypeFileNode, ExcelEncryptionMixin):
    MIMETYPES = [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/encrypted",
        "application/zip",
    ]
    EXTENSIONS = ["xlsx"]


class Xls(MimeTypeFileNode, ExcelEncryptionMixin):
    MIMETYPES = ["application/vnd.ms-excel", "application/CDFV2"]
    EXTENSIONS = ["xls"]


class Csv(MimeTypeFileNode):
    MIMETYPES = ["application/csv", "text/plain"]
    EXTENSIONS = ["csv", "tsv", "txt"]


class Directory(FileNode):
    @property
    def children(self) -> Iterator[FileNode]:
        for child_name in os.listdir(self.name):
            child_path = os.path.join(self.name, child_name)
            node = node_from_file(name=child_path, passwords=self.passwords)
            yield node


class Skip(FileNode):
    pass


def mimetype_from_stream(stream: Optional[IO[bytes]]) -> Optional[str]:
    if stream is None:
        return None

    mimebytes = stream.read()
    mimetype = magic.from_buffer(mimebytes, mime=True)
    stream.seek(0)

    return mimetype


def extension_from_name(name: str) -> Optional[str]:
    _, ext = os.path.splitext(name)
    if ext:
        return ext.lstrip(".")
    else:
        return None


def mimetype_and_extension(
    *, name: Optional[str] = None, stream: Optional[IO[bytes]] = None
) -> Tuple[Optional[str], Optional[str]]:
    if name is not None and stream is None:
        with open(name, "rb") as byte_stream:
            mimetype = mimetype_from_stream(byte_stream)
    else:
        mimetype = mimetype_from_stream(stream)

    if name is None:
        extension = None
    else:
        extension = extension_from_name(name)

    return mimetype, extension


def node_from_file(
    *,
    name: Optional[str] = None,
    stream: Optional[IO[bytes]] = None,
    passwords: Dict[str, str] = {},
) -> FileNode:
    if name is not None and any(pattern in name for pattern in OS_PATTERNS_TO_SKIP):
        return Skip(name=name, stream=stream)

    if name is not None and os.path.isdir(name):
        return Directory(name=name, stream=stream, passwords=passwords)

    mimetype, extension = mimetype_and_extension(name=name, stream=stream)

    for node_type in MimeTypeFileNode.__subclasses__():
        if node_type.is_my_mimetype_or_extension(mimetype, extension):
            node: FileNode = node_type(
                name=name,
                stream=stream,
                mimetype=mimetype,
                extension=extension,
                passwords=passwords,
            )
            return node

    return Skip(name=name, stream=stream, mimetype=mimetype, extension=extension)

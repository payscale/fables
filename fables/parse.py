"""
Define visitor of functions for nodes of the detection tree.
Each visitor will either generate tables based on the node type
or will make a call to its children nodes to generate tables e.g.
a Zip node will look at all of its child files for tables to
generate.

The visitor does inspection on the node to decide what kind of
visitation to do. This is a common technique for implementing
the visitor pattern in Python:

- std lib ast: https://github.com/python/cpython/blob/3.7/Lib/ast.py#L258
- mypy: https://github.com/python/mypy/blob/master/mypy/fastparse.py#L229
- pypy: https://github.com/mozillazg/pypy/blob/master/pypy/interpreter/astcompiler/ast.py#L3675
"""

import clevercsv  # type: ignore
from typing import Any, Dict, IO, Iterable, Optional, Union

import xlrd  # type: ignore
import pandas as pd  # type: ignore
import cchardet as chardet  # type: ignore

from fables.constants import ENCODING_DETECTION_CONFIDENCE_THRESHOLD
from fables.errors import InsufficientEncodingDetectorConfidenceError, ParseError
from fables.results import ParseResult
from fables.table import Table
from fables.tree import FileNode, Directory, Zip, Csv, Xls, Xlsx, Xlsb, Skip


ACCEPTED_DELIMITERS = {",", "\t", ";", ":", "|"}
FALLBACK_DELIMITER = ","
FRACTION_OF_BLANK_HEADERS_ALLOWED = 0.5


def sniff_delimiter(bytesio: IO[bytes], encoding: Optional[str]) -> str:
    encoding = encoding if encoding is not None else "utf-8"
    sample = bytesio.read(1024 * 4).decode(encoding=encoding)
    bytesio.seek(0)
    sniffer = clevercsv.Sniffer()
    dialect = sniffer.sniff(sample, delimiters="".join(ACCEPTED_DELIMITERS))
    return str(dialect.delimiter)


def detect_encoding(bytesio: IO[bytes]) -> str:
    detection = chardet.detect(bytesio.read())
    bytesio.seek(0)
    if detection["confidence"] >= ENCODING_DETECTION_CONFIDENCE_THRESHOLD:
        return str(detection["encoding"])
    else:
        raise InsufficientEncodingDetectorConfidenceError(
            confidence_threshold=ENCODING_DETECTION_CONFIDENCE_THRESHOLD
        )


def _extract_data_frame_from_csv(
    bytesio: IO[bytes], pandas_kwargs: Dict[str, Any]
) -> pd.DataFrame:
    encoding = pandas_kwargs.get("encoding", None)
    try:
        delimiter = sniff_delimiter(bytesio, encoding)
    except clevercsv.Error:
        delimiter = FALLBACK_DELIMITER
    else:
        # clevercsv returns the empty string if no delimiter was found in the
        # file, which is incompatible with pd.read_csv.
        if not delimiter:
            delimiter = FALLBACK_DELIMITER
    df = pd.read_csv(bytesio, skip_blank_lines=True, sep=delimiter, **pandas_kwargs)
    return df


def remove_data_before_header(df: pd.DataFrame, force_numeric: bool) -> pd.DataFrame:
    num_cols = len(df.columns)
    pre_header_row_removal_was_needed = False
    while (
        len(df)
        and
        # Greater than FRACTION_OF_BLANK_HEADERS_ALLOWED of the header names
        # are blank. Note that the initial inferred headers might be
        # 'Unnamed: #', but once we replace the headers with the first row,
        # those missing values will be NaN's.
        len(
            [
                col
                for col in df.columns
                if str(col).startswith("Unnamed: ") or pd.isnull(col)
            ]
        )
        > FRACTION_OF_BLANK_HEADERS_ALLOWED * num_cols
    ):
        pre_header_row_removal_was_needed = True
        # Replace the headers with the first row
        df.columns = df.iloc[0].values
        df.drop(df.index[0], inplace=True)
    if pre_header_row_removal_was_needed:
        if not len(df):
            raise ValueError(
                "Error during pre-header row removal:"
                " Reached end of file with no valid header row found."
            )

        if force_numeric:
            for col in df.columns:
                # Try to convert columns back to numeric type, skipping those that
                # can't be converted. With the initial parse containing pre-header
                # data, all columns will have had a string row containing the
                # read header, so all columns in the DataFrame would be rounded
                # up to string type.
                df[col] = pd.to_numeric(df[col], errors="ignore")
    return df


def post_process_dataframe(df: pd.DataFrame, force_numeric: bool) -> pd.DataFrame:
    # Remove columns that have no header and have only null data.
    for col in df.columns:
        if (pd.isnull(col) or str(col).startswith("Unnamed: ")) and df[
            col
        ].isnull().all():
            df.drop(col, axis=1, inplace=True)
    # Remove data before headers.
    df = remove_data_before_header(df, force_numeric)
    num_rows_before = len(df)
    if num_rows_before:
        # Remove rows that have only nulls.
        df.dropna(how="all", axis=0, inplace=True)
        # Retain 0-based index.
        num_rows_after = len(df)
        df.index = range(num_rows_after)

    return df


def parse_csv(
    bytesio: IO[bytes], *, force_numeric: bool = True, pandas_kwargs: Dict[str, Any]
) -> pd.DataFrame:
    user_supplied_encoding = pandas_kwargs.get("encoding")
    try:
        df = _extract_data_frame_from_csv(bytesio, pandas_kwargs)
    except UnicodeDecodeError:
        if user_supplied_encoding is not None:
            raise
        else:
            bytesio.seek(0)
            detected_encoding = detect_encoding(bytesio)
            df = _extract_data_frame_from_csv(
                bytesio, {"encoding": detected_encoding, **pandas_kwargs}
            )
    df = post_process_dataframe(df, force_numeric)
    return df


def parse_excel_sheet(
    excel_file: pd.ExcelFile,
    sheet: str,
    *,
    force_numeric: bool = True,
    pandas_kwargs: Dict[str, Any],
) -> pd.DataFrame:
    df = excel_file.parse(sheet, skip_blank_lines=True, **pandas_kwargs)
    df = post_process_dataframe(df, force_numeric)
    return df


class ParseVisitor:
    def __init__(
        self, *, force_numeric: bool = True, pandas_kwargs: Dict[str, Any]
    ) -> None:
        self.force_numeric = force_numeric
        self.pandas_kwargs = pandas_kwargs

    def visit(self, node: FileNode) -> Iterable[ParseResult]:
        visitor_method_name = "visit_" + node.__class__.__name__
        visitor_method = getattr(self, visitor_method_name)
        yield from visitor_method(node)

    def visit_Csv(self, node: Csv) -> Iterable[ParseResult]:
        tables = []
        errors = []
        with node.stream as bytesio:
            try:
                df = parse_csv(
                    bytesio,
                    force_numeric=self.force_numeric,
                    pandas_kwargs=self.pandas_kwargs,
                )
                table = Table(df=df, name=node.name)
                tables.append(table)
            except Exception as e:
                parse_error = ParseError(
                    message=str(e), exception_type=type(e), name=node.name
                )
                errors.append(parse_error)
        yield ParseResult(name=node.name, tables=tables, errors=errors)

    def _visit_excel(self, node: Union[Xls, Xlsx, Xlsb]) -> Iterable[ParseResult]:
        tables = []
        errors = []

        with node.stream as bytesio:
            try:
                if isinstance(node, Xlsb):
                    excel_file = pd.ExcelFile(bytesio.read(), engine="pyxlsb")
                else:
                    workbook = xlrd.open_workbook(file_contents=bytesio.read())
                    excel_file = pd.ExcelFile(workbook, engine="xlrd")
                sheets = excel_file.sheet_names
                for sheet in sheets:
                    try:
                        df = parse_excel_sheet(
                            excel_file,
                            sheet,
                            force_numeric=self.force_numeric,
                            pandas_kwargs=self.pandas_kwargs,
                        )
                        table = Table(df=df, name=node.name, sheet=sheet)
                        tables.append(table)
                    except Exception as e:
                        error = ParseError(
                            message=str(e),
                            exception_type=type(e),
                            name=node.name,
                            sheet=sheet,
                        )
                        errors.append(error)

            except Exception as e:
                error = ParseError(
                    message=str(e), exception_type=type(e), name=node.name
                )
                errors.append(error)

        yield ParseResult(name=node.name, tables=tables, errors=errors)

    def visit_Xls(self, node: Xls) -> Iterable[ParseResult]:
        yield from self._visit_excel(node)

    def visit_Xlsx(self, node: Xlsx) -> Iterable[ParseResult]:
        yield from self._visit_excel(node)

    def visit_Xlsb(self, node: Xlsb) -> Iterable[ParseResult]:
        yield from self._visit_excel(node)

    def visit_Zip(self, node: Zip) -> Iterable[ParseResult]:
        for child in node.children:
            yield from self.visit(child)

    def visit_Directory(self, node: Directory) -> Iterable[ParseResult]:
        for child in node.children:
            yield from self.visit(child)

    def visit_Skip(self, _node: Skip) -> Iterable[ParseResult]:
        yield from []

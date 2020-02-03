import os
import xml

import numpy as np
import pytest
import pandas as pd

from tests.context import fables
from tests.integration.constants import DATA_DIR


# a,b
# 1,2
# 3,4
AB_DF = pd.DataFrame(columns=["a", "b"], data=[[1, 2], [3, 4]])

# a,b,c
# 1,2,3
# 4,5,6
ABC_DF = pd.DataFrame(columns=["a", "b", "c"], data=[[1, 2, 3], [4, 5, 6]])


def _it_parses_a_csv(csv_name, expected_df):
    parse_results = list(fables.parse(io=csv_name))
    assert len(parse_results) == 1

    parse_result = parse_results[0]
    assert parse_result.name == csv_name
    assert len(parse_result.errors) == 0
    assert len(parse_result.tables) == 1

    table = parse_result.tables[0]
    assert table.name == csv_name
    assert table.sheet is None

    pd.testing.assert_frame_equal(table.df, expected_df, check_dtype=False)

    assert not parse_results[0].errors


def test_it_parses_a_csv():
    csv_name = os.path.join(DATA_DIR, "basic.csv")
    _it_parses_a_csv(csv_name, AB_DF)


def test_it_parses_a_csv_with_only_a_header():
    csv_name = os.path.join(DATA_DIR, "only_header.csv")
    expected_df = pd.DataFrame(columns=["a", "b"], data=[])
    _it_parses_a_csv(csv_name, expected_df)


def test_stream_parse_is_the_same_as_disk_parse():
    csv_name = os.path.join(DATA_DIR, "basic.csv")

    with open(csv_name, "rb") as buffered_io:
        stream_results = list(fables.parse(io=buffered_io))

    disk_results = list(fables.parse(io=csv_name))

    assert len(stream_results) == len(disk_results)
    assert len(stream_results[0].tables) == len(disk_results[0].tables)

    stream_result = stream_results[0]
    disk_result = disk_results[0]
    assert stream_result.name == csv_name
    assert disk_result.name == csv_name

    stream_table = stream_result.tables[0]
    disk_table = disk_result.tables[0]

    assert stream_table.name == disk_table.name
    pd.testing.assert_frame_equal(stream_table.df, disk_table.df, check_dtype=False)


def _it_parses_an_excel_file_with_one_sheet(excel_name, expected_df, passwords={}):
    parse_results = list(fables.parse(io=excel_name, passwords=passwords))

    assert len(parse_results) == 1

    parse_result = parse_results[0]
    assert parse_result.name == excel_name
    tables = parse_result.tables
    errors = parse_result.errors
    assert len(tables) == 1
    assert len(errors) == 0

    table = tables[0]
    assert table.name == excel_name
    assert table.sheet == "Sheet1"

    pd.testing.assert_frame_equal(table.df, expected_df, check_dtype=False)


def test_it_parses_a_xlsx_with_one_sheet():
    xlsx_name = os.path.join(DATA_DIR, "basic.xlsx")
    _it_parses_an_excel_file_with_one_sheet(xlsx_name, AB_DF)

def test_it_parses_a_xlsb_with_one_sheet():
    xlsb_name = os.path.join(DATA_DIR, "basic.xlsb")
    _it_parses_an_excel_file_with_one_sheet(xlsb_name, AB_DF)

def test_it_parses_a_xlsb_with_only_a_header():
    only_xlsb_name = os.path.join(DATA_DIR, "only_header.xlsb")
    expected_df = pd.DataFrame(columns=["a", "b"], data=[])
    _it_parses_an_excel_file_with_one_sheet(only_xlsb_name, expected_df)

def test_it_parses_a_xlsb_with_many_sheets():
    xlsb_name = os.path.join(DATA_DIR, "two_sheets.xlsb")

    parse_results = list(fables.parse(io=xlsb_name))

    assert len(parse_results) == 1

    parse_result = parse_results[0]
    assert parse_result.name == xlsb_name
    tables = parse_result.tables
    errors = parse_result.errors
    assert len(tables) == 2
    assert len(errors) == 0

    table1, table2 = tables
    assert table1.name == xlsb_name
    assert table1.sheet == "Sheet1"
    assert table2.name == xlsb_name
    assert table2.sheet == "Sheet2"

    expected_sheet1_df = AB_DF
    pd.testing.assert_frame_equal(table1.df, expected_sheet1_df, check_dtype=False)

    expected_sheet2_df = pd.DataFrame(columns=["c", "d"], data=[[5, 6], [7, 8]])
    pd.testing.assert_frame_equal(table2.df, expected_sheet2_df, check_dtype=False)


def test_it_parses_a_xlsx_with_many_sheets():
    xlsx_name = os.path.join(DATA_DIR, "two_sheets.xlsx")

    parse_results = list(fables.parse(io=xlsx_name))

    assert len(parse_results) == 1

    parse_result = parse_results[0]
    assert parse_result.name == xlsx_name
    tables = parse_result.tables
    errors = parse_result.errors
    assert len(tables) == 2
    assert len(errors) == 0

    table1, table2 = tables
    assert table1.name == xlsx_name
    assert table1.sheet == "Sheet1"
    assert table2.name == xlsx_name
    assert table2.sheet == "Sheet2"

    expected_sheet1_df = AB_DF
    pd.testing.assert_frame_equal(table1.df, expected_sheet1_df, check_dtype=False)

    expected_sheet2_df = pd.DataFrame(columns=["c", "d"], data=[[5, 6], [7, 8]])
    pd.testing.assert_frame_equal(table2.df, expected_sheet2_df, check_dtype=False)


def test_it_parses_a_xlsx_with_only_a_header():
    xlsx_name = os.path.join(DATA_DIR, "only_header.xlsx")

    parse_results = list(fables.parse(io=xlsx_name))

    assert len(parse_results) == 1

    parse_result = parse_results[0]
    assert parse_result.name == xlsx_name
    tables = parse_result.tables
    errors = parse_result.errors
    assert len(tables) == 1
    assert len(errors) == 0

    table = tables[0]
    assert table.sheet == "Sheet1"
    assert table.name == xlsx_name

    expected_df = pd.DataFrame(columns=["a", "b"], data=[])
    pd.testing.assert_frame_equal(table.df, expected_df, check_dtype=False)


def test_it_parses_a_xlsx_with_only_one_cell_filled():
    xlsx_name = os.path.join(DATA_DIR, "only_one_cell_filled.xlsx")

    parse_results = list(fables.parse(io=xlsx_name))

    assert len(parse_results) == 1

    parse_result = parse_results[0]
    assert parse_result.name == xlsx_name
    tables = parse_result.tables
    errors = parse_result.errors
    assert len(tables) == 1
    assert len(errors) == 0

    table = tables[0]
    assert table.sheet == "Sheet1"
    assert table.name == xlsx_name

    expected_df = pd.DataFrame(columns=["a"], data=[])
    pd.testing.assert_frame_equal(table.df, expected_df, check_dtype=False)


def test_it_parses_a_xls_with_one_sheet():
    xls_name = os.path.join(DATA_DIR, "basic.xls")
    _it_parses_an_excel_file_with_one_sheet(xls_name, AB_DF)


def test_it_parses_a_xls_with_many_sheets():
    xls_name = os.path.join(DATA_DIR, "two_sheets.xls")

    parse_results = list(fables.parse(io=xls_name))

    assert len(parse_results) == 1

    parse_result = parse_results[0]
    assert parse_result.name == xls_name
    tables = parse_result.tables
    errors = parse_result.errors
    assert len(tables) == 2
    assert len(errors) == 0

    table1, table2 = tables
    assert table1.name == xls_name
    assert table1.sheet == "Sheet1"
    assert table2.name == xls_name
    assert table2.sheet == "Sheet2"

    expected_sheet1_df = AB_DF
    pd.testing.assert_frame_equal(table1.df, expected_sheet1_df, check_dtype=False)

    expected_sheet2_df = pd.DataFrame(columns=["c", "d"], data=[[5, 6], [7, 8]])
    pd.testing.assert_frame_equal(table2.df, expected_sheet2_df, check_dtype=False)


def _validate_basic_csv_and_basic_xlsx_together(parse_results, child_names):
    assert len(parse_results) == 2
    csv_name = [cn for cn in child_names if cn.endswith("csv")][0]
    xlsx_name = [cn for cn in child_names if cn.endswith("xlsx")][0]

    csv_results = [pr for pr in parse_results if pr.name == csv_name]
    xlsx_results = [pr for pr in parse_results if pr.name == xlsx_name]

    assert len(csv_results) == 1
    assert len(xlsx_results) == 1

    csv_result = csv_results[0]
    xlsx_result = xlsx_results[0]

    assert len(csv_result.tables) == 1
    assert len(csv_result.errors) == 0
    assert len(xlsx_result.tables) == 1
    assert len(xlsx_result.errors) == 0

    csv_table = csv_result.tables[0]
    pd.testing.assert_frame_equal(csv_table.df, AB_DF, check_dtype=False)
    assert csv_table.name == csv_name

    xlsx_table = xlsx_result.tables[0]
    pd.testing.assert_frame_equal(xlsx_table.df, AB_DF, check_dtype=False)
    assert xlsx_table.name == xlsx_name


def test_it_parses_all_files_in_a_directory():
    """
    sub_dir/
        basic.csv
        basic.xlsx
    """
    sub_dir = os.path.join(DATA_DIR, "sub_dir")
    parse_results = list(fables.parse(io=sub_dir))
    child_names = [
        os.path.join(sub_dir, "basic.csv"),
        os.path.join(sub_dir, "basic.xlsx"),
    ]
    _validate_basic_csv_and_basic_xlsx_together(parse_results, child_names)


def _it_parses_flat_files_in_a_basic_zip(zip_file, zip_path):
    parse_results = list(fables.parse(io=zip_path))

    # NOTE: The name fields on files inside a zip files do not
    #       retain the full path.
    child_names = [
        os.path.join(zip_file, child_file) for child_file in ["basic.csv", "basic.xlsx"]
    ]
    _validate_basic_csv_and_basic_xlsx_together(parse_results, child_names)


def test_it_parses_flat_files_in_a_basic_zip():
    """
    basic.zip
        basic.csv
        basic.xlsx
    """
    zip_file = "basic.zip"
    zip_path = os.path.join(DATA_DIR, zip_file)
    _it_parses_flat_files_in_a_basic_zip(zip_file, zip_path)


def _validate_side_xls_file(xls_result, expected_name):
    # validate basic.xls
    assert xls_result.name == expected_name
    assert len(xls_result.errors) == 0
    assert len(xls_result.tables) == 1

    table = xls_result.tables[0]
    assert table.name == expected_name
    assert table.sheet == "Sheet1"

    pd.testing.assert_frame_equal(table.df, AB_DF, check_dtype=False)


def test_it_parses_files_in_a_directory_inside_a_zip():
    """
    sub_dir.zip
        basic.xls
        sub_dir/basic.csv
        sub_dir/basic.xlsx
    """
    zip_file = "sub_dir.zip"
    zip_path = os.path.join(DATA_DIR, zip_file)

    parse_results = list(fables.parse(io=zip_path))

    assert len(parse_results) == 3

    xls_name = os.path.join(zip_file, "basic.xls")
    xls_result = [pr for pr in parse_results if pr.name == xls_name][0]

    # NOTE: paths inside the zipfile lib always use unix paths
    csv_name = os.path.join(zip_file, "sub_dir/basic.csv")
    csv_result = [pr for pr in parse_results if pr.name == csv_name][0]

    xlsx_name = os.path.join(zip_file, "sub_dir/basic.xlsx")
    xlsx_result = [pr for pr in parse_results if pr.name == xlsx_name][0]

    _validate_side_xls_file(xls_result, xls_name)
    _validate_basic_csv_and_basic_xlsx_together(
        [csv_result, xlsx_result], [csv_name, xlsx_name]
    )


def test_it_parses_files_in_a_zip_in_a_zip():
    """
    nested.zip
        basic.zip
            basic.csv
            basic.xlsx
        basic.xls
    """
    zip_file = "nested.zip"
    zip_path = os.path.join(DATA_DIR, zip_file)
    inner_zip_file = "basic.zip"

    parse_results = list(fables.parse(io=zip_path))

    assert len(parse_results) == 3

    xls_name = os.path.join(zip_file, "basic.xls")
    xls_result = [pr for pr in parse_results if pr.name == xls_name][0]

    # NOTE: paths inside the zipfile lib always use unix paths
    csv_name = os.path.join(inner_zip_file, "basic.csv")
    csv_result = [pr for pr in parse_results if pr.name == csv_name][0]

    xlsx_name = os.path.join(inner_zip_file, "basic.xlsx")
    xlsx_result = [pr for pr in parse_results if pr.name == xlsx_name][0]

    _validate_side_xls_file(xls_result, xls_name)
    _validate_basic_csv_and_basic_xlsx_together(
        [csv_result, xlsx_result], [csv_name, xlsx_name]
    )


def test_it_parses_files_in_an_encrypted_zip_with_password():
    """
    encrypted.zip
        basic.csv
        basic.xlsx
    """
    zip_file = "encrypted.zip"
    zip_path = os.path.join(DATA_DIR, zip_file)

    parse_results = list(fables.parse(io=zip_path, passwords={zip_file: "fables"}))
    child_names = [
        os.path.join(zip_file, child_file) for child_file in ["basic.csv", "basic.xlsx"]
    ]
    _validate_basic_csv_and_basic_xlsx_together(parse_results, child_names)


def test_it_parses_files_in_an_encrypted_xlsx():
    xlsx_name = os.path.join(DATA_DIR, "encrypted.xlsx")
    _it_parses_an_excel_file_with_one_sheet(
        xlsx_name, AB_DF, passwords={xlsx_name: "fables"}
    )


def test_it_parses_files_in_an_encrypted_xls():
    xls_name = os.path.join(DATA_DIR, "encrypted.xls")
    _it_parses_an_excel_file_with_one_sheet(
        xls_name, AB_DF, passwords={xls_name: "fables"}
    )


def test_it_parses_nested_encrypted_files():
    """
    nested_encrypted.zip       - pw: feebles
        encrypted_xlsx_csv.zip - pw: foobles
            basic.csv
            encrypted.xlsx     - pw: fables
        encrypted.xls          - pw: fables
    """
    nested_encrypted_name = os.path.join(DATA_DIR, "nested_encrypted.zip")
    parse_results = list(
        fables.parse(
            io=nested_encrypted_name,
            passwords={
                nested_encrypted_name: "feebles",
                "encrypted_xlsx_csv.zip": "foobles",
                "encrypted.xlsx": "fables",
                "encrypted.xls": "fables",
            },
        )
    )
    assert len(parse_results) == 3

    for filename in ["basic.csv", "encrypted.xlsx", "encrypted.xls"]:
        result = [pr for pr in parse_results if pr.name.endswith(filename)][0]

        assert len(result.errors) == 0
        assert len(result.tables) == 1

        table = result.tables[0]
        assert table.name.endswith(filename)
        if not table.name.endswith("csv"):
            assert table.sheet == "Sheet1"
        else:
            assert table.sheet is None
        pd.testing.assert_frame_equal(table.df, AB_DF, check_dtype=False)


def test_it_finds_no_tables_in_an_invalid_csv_plain_text_file():
    """Invalid plain text csv content
    ---------------
    header
    there are two hard things in computer science
    off by one errors, naming things, and cache invalidation
    """
    txt_file_name = os.path.join(DATA_DIR, "invalid_plain_text.txt")
    parse_results = list(fables.parse(io=txt_file_name))
    assert len(parse_results) == 1
    parse_result = parse_results[0]
    assert len(parse_result.tables) == 0
    assert len(parse_result.errors) == 1
    error = parse_result.errors[0]
    assert error.name == txt_file_name
    assert error.exception_type is pd.errors.ParserError
    assert "Error tokenizing data." in error.message


def test_it_finds_tables_in_a_valid_csv_plain_text_file():
    """Valid plain text csv content
    ---------------
    some text
    some other text
    """
    txt_file_name = os.path.join(DATA_DIR, "valid_plain_text.txt")
    parse_results = list(fables.parse(io=txt_file_name))
    assert len(parse_results) == 1
    parse_result = parse_results[0]
    assert len(parse_result.tables) == 1
    assert len(parse_result.errors) == 0
    table = parse_result.tables[0]
    assert table.name == txt_file_name
    assert table.sheet is None
    expected_df = pd.DataFrame(columns=["some text"], data=[["some other text"]])
    pd.testing.assert_frame_equal(table.df, expected_df, check_dtype=False)


def test_it_finds_no_tables_in_a_png_file():
    png_name = os.path.join(DATA_DIR, "terminal.png")
    parse_results = list(fables.parse(io=png_name))
    assert len(parse_results) == 0


def test_it_raises_a_value_error_for_a_file_name_that_does_not_exist_on_disk():
    missing_name = os.path.join(DATA_DIR, "missing.csv")
    with pytest.raises(ValueError) as e:
        for _ in fables.parse(io=missing_name):
            pass

    assert "parse" in str(e.value)


def test_it_raises_a_type_error_for_stream_not_read_in_bytes_mode():
    csv_name = os.path.join(DATA_DIR, "basic.csv")

    with open(csv_name, "r") as textio:
        with pytest.raises(TypeError) as e:
            for _ in fables.parse(io=textio):
                pass

    assert "parse" in str(e.value)
    assert "io.BufferedIOBase" in str(e.value)


def test_it_creates_a_parse_error_for_malformed_csv():
    csv_name = os.path.join(DATA_DIR, "malformed.csv")

    parse_results = list(fables.parse(io=csv_name))
    assert len(parse_results) == 1

    parse_result = parse_results[0]
    assert len(parse_result.tables) == 0
    assert len(parse_result.errors) == 1

    error = parse_result.errors[0]
    assert (
        error.message
        == "Error tokenizing data. C error: Expected 2 fields in line 3, saw 3\n"
    )
    assert error.exception_type is pd.errors.ParserError
    assert error.name == csv_name


def test_it_creates_a_parse_error_for_corrupt_file():
    """To reproduce, open file in xlsx file in a text editor,
    and delete some characters from the worksheet xml file."""
    corrupt_xlsx_name = os.path.join(DATA_DIR, "corrupt.xlsx")

    parse_results = list(fables.parse(io=corrupt_xlsx_name))
    assert len(parse_results) == 1

    parse_result = parse_results[0]
    assert parse_result.name == corrupt_xlsx_name

    tables = parse_result.tables
    errors = parse_result.errors
    assert len(tables) == 0
    assert len(errors) == 1

    error = errors[0]
    assert error.name == corrupt_xlsx_name

    assert error.exception_type is xml.etree.ElementTree.ParseError
    assert "not well-formed" in error.message


@pytest.mark.parametrize(
    "file_name",
    [
        "more_null_middle_cols_than_non_null_cols.csv",
        "more_null_middle_cols_than_non_null_cols.xlsx",
    ],
)
def test_it_creates_a_parse_error_for_no_valid_headers(file_name):
    file_path = os.path.join(DATA_DIR, file_name)

    parse_results = list(fables.parse(io=file_path))
    assert len(parse_results) == 1

    parse_result = parse_results[0]
    assert parse_result.name == file_path

    tables = parse_result.tables
    assert len(tables) == 0

    errors = parse_result.errors
    assert len(errors) == 1

    error = errors[0]
    assert error.name == file_path

    assert error.exception_type is ValueError
    assert "Error during pre-header row removal" in error.message


def test_it_parses_a_xls_with_no_extension():
    xls_name = os.path.join(DATA_DIR, "basic_xls_with_no_extension")
    _it_parses_an_excel_file_with_one_sheet(xls_name, AB_DF)


def test_it_parses_a_xlsx_with_no_extension():
    xlsx_name = os.path.join(DATA_DIR, "basic_xlsx_with_no_extension")
    _it_parses_an_excel_file_with_one_sheet(xlsx_name, AB_DF)


def test_it_parses_files_in_a_zip_with_no_extension():
    zip_name = "basic_zip_with_no_extension"
    zip_path = os.path.join(DATA_DIR, zip_name)
    _it_parses_flat_files_in_a_basic_zip(zip_name, zip_path)


def test_it_parses_a_csv_with_missing_opening_rows():
    """File content (first two rows have no data):


    a,b
    1,3
    2,4
    """
    csv_name = "missing_opening_rows.csv"
    csv_path = os.path.join(DATA_DIR, csv_name)
    _it_parses_a_csv(csv_path, AB_DF)


def test_it_parses_a_semicolon_seperated_csv():
    """File content:
    a;b
    1;2
    3;4
    """
    csv_name = "basic_semicolon_sep.csv"
    csv_path = os.path.join(DATA_DIR, csv_name)
    _it_parses_a_csv(csv_path, AB_DF)


def test_it_parses_a_tab_seperated_csv():
    """File content:
    a	b
    1	2
    3	4
    """
    csv_name = "basic_tab_sep.tsv"
    csv_path = os.path.join(DATA_DIR, csv_name)
    _it_parses_a_csv(csv_path, AB_DF)


@pytest.mark.parametrize(
    "file_name,test_callable,expected_df",
    [
        ("null_opening_rows.csv", _it_parses_a_csv, AB_DF),
        ("null_opening_rows.xlsx", _it_parses_an_excel_file_with_one_sheet, AB_DF),
    ],
)
def test_it_parses_files_with_null_opening_rows(file_name, test_callable, expected_df):
    """File content:
    ,
    ,
    a,b
    1,3
    2,4
    """
    path = os.path.join(DATA_DIR, file_name)
    test_callable(path, expected_df)


@pytest.mark.parametrize(
    "file_name,test_callable,expected_df",
    [
        ("null_leading_and_trailing_cols.csv", _it_parses_a_csv, AB_DF),
        (
            "null_leading_and_trailing_cols.xlsx",
            _it_parses_an_excel_file_with_one_sheet,
            AB_DF,
        ),
        (
            "null_leading_col_with_left_header.xlsx",
            _it_parses_an_excel_file_with_one_sheet,
            ABC_DF,
        ),
        (
            "null_leading_col_with_right_header.xlsx",
            _it_parses_an_excel_file_with_one_sheet,
            ABC_DF,
        ),
    ],
)
def test_it_parses_files_with_null_leading_and_trailing_cols(
    file_name, test_callable, expected_df
):
    """File content:
    ,a,b,
    ,1,2,
    ,3,4,

    or

    ,header 1,,,
    ,header 2,,,
    ,,,,
    ,a,b,c,
    ,1,2,3,
    ,4,5,6,

    or

    ,,,header 1,
    ,,,header 2,
    ,,,,
    ,a,b,c,
    ,1,2,3,
    ,4,5,6,
    """
    path = os.path.join(DATA_DIR, file_name)
    test_callable(path, expected_df)


@pytest.mark.parametrize(
    "file_name,test_callable,expected_df",
    [
        ("null_middle_cols.csv", _it_parses_a_csv, AB_DF),
        ("null_middle_cols.xlsx", _it_parses_an_excel_file_with_one_sheet, AB_DF),
    ],
)
def test_it_parses_files_with_null_middle_cols(file_name, test_callable, expected_df):
    """File content:
    a,,b
    1,,2
    3,,4
    """
    path = os.path.join(DATA_DIR, file_name)
    test_callable(path, expected_df)


@pytest.mark.parametrize(
    "file_name,test_callable,expected_df",
    [
        ("null_middle_rows.csv", _it_parses_a_csv, AB_DF),
        ("null_middle_rows.xlsx", _it_parses_an_excel_file_with_one_sheet, AB_DF),
    ],
)
def test_it_parses_files_with_null_middle_rows(file_name, test_callable, expected_df):
    """File content:
    a,b
    1,2
    ,
    3,4
    """
    path = os.path.join(DATA_DIR, file_name)
    test_callable(path, expected_df)


@pytest.mark.parametrize(
    "file_name,test_callable,expected_df",
    [
        ("noisy_opening_rows.csv", _it_parses_a_csv, ABC_DF),
        ("noisy_opening_rows.xlsx", _it_parses_an_excel_file_with_one_sheet, ABC_DF),
    ],
)
def test_it_parses_files_with_noisy_opening_rows(file_name, test_callable, expected_df):
    """File content:
    x,,
    ,y,
    ,,
    a,b,c
    1,2,3
    4,5,6
    """
    path = os.path.join(DATA_DIR, file_name)
    test_callable(path, expected_df)


@pytest.mark.parametrize(
    "file_name,pandas_kwargs",
    [
        ("na.xlsx", {"keep_default_na": False}),
        ("na.csv", {"keep_default_na": False}),
        ("na.xlsx", {}),
        ("na.csv", {}),
    ],
)
def test_it_parses_files_using_pandas_kwargs(file_name, pandas_kwargs):
    """
    Will parse to this if pandas kwarg keep_default_na is False:
    a,b,c
    1,2,N/A
    4,5,N/A

    Will parse to this if pandas kwarg keep_default_na is True
    (it is True by default):
    a,b,c
    1,2,NaN
    4,5,NaN
    """
    path = os.path.join(DATA_DIR, file_name)
    parse_results = list(fables.parse(path, pandas_kwargs=pandas_kwargs))
    assert len(parse_results) == 1
    parse_result = parse_results[0]
    assert len(parse_result.errors) == 0
    tables = parse_result.tables
    assert len(tables) == 1

    df = tables[0].df

    if pandas_kwargs == {}:
        expected_df = pd.DataFrame(
            columns=["a", "b", "c"], data=[[1, 2, np.nan], [4, 5, np.nan]]
        )
        pd.testing.assert_frame_equal(df, expected_df, check_dtype=False)
    else:
        assert pandas_kwargs == {"keep_default_na": False}
        expected_df = pd.DataFrame(
            columns=["a", "b", "c"], data=[[1, 2, "N/A"], [4, 5, "N/A"]]
        )
        pd.testing.assert_frame_equal(df, expected_df, check_dtype=False)


string_df = pd.DataFrame(
    columns=["x", "y", "z"],
    data=[["001", "a", "b"], ["002", "a", "b"], ["003", "a", "b"]],
)
numeric_df = pd.DataFrame(
    columns=["x", "y", "z"], data=[[1, "a", "b"], [2, "a", "b"], [3, "a", "b"]]
)


@pytest.mark.parametrize(
    "file_name,force_numeric,pandas_kwargs,expected_df",
    [
        ("string_vs_numeric.csv", False, {}, numeric_df),
        ("string_vs_numeric.csv", False, {"dtype": str}, string_df),
        ("string_vs_numeric.csv", True, {}, numeric_df),
        ("string_vs_numeric.csv", True, {"dtype": str}, string_df),
        ("string_vs_numeric_noise_before_header.csv", False, {}, string_df),
        ("string_vs_numeric_noise_before_header.csv", False, {"dtype": str}, string_df),
        ("string_vs_numeric_noise_before_header.csv", True, {}, numeric_df),
        ("string_vs_numeric_noise_before_header.csv", True, {"dtype": str}, numeric_df),
        ("string_vs_numeric.xlsx", False, {}, numeric_df),
        ("string_vs_numeric.xlsx", False, {"dtype": str}, string_df),
        ("string_vs_numeric.xlsx", True, {}, numeric_df),
        ("string_vs_numeric.xlsx", True, {"dtype": str}, string_df),
        ("string_vs_numeric_noise_before_header.xlsx", False, {}, string_df),
        (
            "string_vs_numeric_noise_before_header.xlsx",
            False,
            {"dtype": str},
            string_df,
        ),
        ("string_vs_numeric_noise_before_header.xlsx", True, {}, numeric_df),
        (
            "string_vs_numeric_noise_before_header.xlsx",
            True,
            {"dtype": str},
            numeric_df,
        ),
    ],
)
def test_force_numeric(file_name, force_numeric, pandas_kwargs, expected_df):
    """
    a,,
    ,,
    ,,
    x,y,z
    001,a,b
    002,a,b
    003,a,b

    and

    x,y,z
    001,a,b
    002,a,b
    003,a,b
    """
    path = os.path.join(DATA_DIR, file_name)
    parse_results = list(
        fables.parse(path, force_numeric=force_numeric, pandas_kwargs=pandas_kwargs)
    )
    assert len(parse_results) == 1
    parse_result = parse_results[0]
    assert len(parse_result.errors) == 0
    tables = parse_result.tables
    assert len(tables) == 1

    df = tables[0].df

    pd.testing.assert_frame_equal(df, expected_df, check_dtype=False)

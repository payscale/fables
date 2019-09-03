import os

import pytest

from tests.context import fables
from tests.integration.constants import DATA_DIR


@pytest.mark.parametrize(
    "name,node_type,mimetype,extension,num_children",
    [
        ("basic.csv", fables.Csv, "text/plain", "csv", 0),
        (
            "basic.xlsx",
            fables.Xlsx,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xlsx",
            0,
        ),  # noqa: E501
        ("encrypted.xlsx", fables.Xlsx, "application/encrypted", "xlsx", 0),
        ("basic.xls", fables.Xls, "application/vnd.ms-excel", "xls", 0),
        ("encrypted.xls", fables.Xls, "application/vnd.ms-excel", "xls", 0),
        ("basic.zip", fables.Zip, "application/zip", "zip", 2),
        ("encrypted.zip", fables.Zip, "application/zip", "zip", 0),
        ("sub_dir", fables.Directory, None, None, 2),
        ("valid_plain_text.txt", fables.Csv, "text/plain", "txt", 0),
        ("invalid_plain_text.txt", fables.Csv, "text/plain", "txt", 0),
        ("terminal.png", fables.Skip, "image/png", "png", 0),
        (os.path.join("__MACOSX", "basic.csv"), fables.Skip, None, None, 0),
    ],
)
def test_it_detects_file_metadata(name, node_type, mimetype, extension, num_children):
    path = os.path.join(DATA_DIR, name)
    node = fables.detect(io=path)

    assert isinstance(node, node_type)
    assert node.mimetype == mimetype
    assert node.extension == extension
    assert len(list(node.children)) == num_children


@pytest.mark.parametrize(
    "name,expected_to_be_encrypted",
    [
        ("basic.csv", False),
        ("encrypted.zip", True),
        ("basic.zip", False),
        ("encrypted.xlsx", True),
        ("basic.xlsx", False),
        ("encrypted.xls", True),
        ("basic.xls", False),
    ],
)
def test_it_detects_when_a_file_is_encrypted(name, expected_to_be_encrypted):
    path = os.path.join(DATA_DIR, name)
    node = fables.detect(io=path)
    assert node.encrypted is expected_to_be_encrypted


def test_it_raises_a_value_error_for_a_file_name_that_does_not_exist_on_disk():
    missing_name = os.path.join(DATA_DIR, "missing.csv")

    with pytest.raises(ValueError) as e:
        fables.detect(io=missing_name)

    exception_msg = str(e.value)
    assert "detect" in exception_msg


def test_it_raises_a_type_error_for_stream_not_read_in_bytes_mode():
    csv_name = os.path.join(DATA_DIR, "basic.csv")

    with open(csv_name, "r") as textio:
        with pytest.raises(TypeError) as e:
            fables.detect(io=textio)

    exception_msg = str(e.value)
    assert "detect" in exception_msg
    assert "io.BufferedIOBase" in exception_msg

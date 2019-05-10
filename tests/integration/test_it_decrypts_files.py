import os
import pytest

from tests.context import fables
from tests.integration.constants import DATA_DIR


@pytest.mark.parametrize(
    "name,password,expected_to_be_encrypted",
    [
        ("encrypted.xlsx", "fables", False),
        ("encrypted.xlsx", "foobles", True),
        ("encrypted.xls", "fables", False),
        ("encrypted.xls", "foobles", True),
        ("encrypted.zip", "fables", False),
        ("encrypted.zip", "foobles", True),
        ("basic.csv", "fables", False),
        ("basic.xlsx", "fables", False),
        ("basic.xls", "fables", False),
        ("basic.zip", "fables", False),
    ],
)
def test_it_unlocks_files_when_the_password_is_correct(
    name, password, expected_to_be_encrypted
):
    path = os.path.join(DATA_DIR, name)

    # test dictionary passed passwords
    node = fables.detect(path, passwords={path: password})
    assert node.password == password
    assert node.passwords == {path: password}
    assert node.encrypted is expected_to_be_encrypted

    # test string passed password
    node = fables.detect(path, password=password)
    assert node.password == password
    assert node.passwords == {path: password}
    assert node.encrypted is expected_to_be_encrypted


def test_it_raises_an_exception_when_decrypting_a_corrupt_file():
    corrupt_xlsx_path = os.path.join(DATA_DIR, "corrupt.xlsx")
    with pytest.raises(RuntimeError) as e:
        with open(corrupt_xlsx_path, "rb") as corrupt_xlsx_stream:
            node = fables.detect(io=corrupt_xlsx_stream)
            with node.stream as node_stream:
                node.decrypt(node_stream, "fables")

    exception_msg = str(e)
    assert corrupt_xlsx_path in exception_msg
    assert "Unexpected exception" in exception_msg

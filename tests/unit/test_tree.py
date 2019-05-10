import pytest

from tests.context import fables


@pytest.mark.parametrize(
    "name,expected_extension",
    [
        ("basic.csv", "csv"),
        ("basic.csv.xlsx", "xlsx"),
        ("basic", None),
        (".gitignore", None),
    ],
)
def test_extension_from_name(name, expected_extension):
    assert fables.tree.extension_from_name(name) == expected_extension


def test_stream_manager_raises_runtime_error_for_only_none_args():
    with pytest.raises(RuntimeError) as e:
        with fables.StreamManager(name=None, stream=None):
            pass

    exception_message = str(e)
    assert "'name'" in exception_message
    assert "'stream'" in exception_message
    assert "io.BufferedIOBase" in exception_message


@pytest.mark.parametrize(
    "name,passwords,expected_password",
    [
        (
            # it does not assign a password when the file doesn't have a name
            None,
            {"encrypted.zip": "fables"},
            None,
        ),
        (
            # it does not assign a password when no passwords are provided
            "sub_dir/encrypted.zip",
            {},
            None,
        ),
        (
            # it assigns a password for a matching file name
            "sub_dir/encrypted.zip",
            {"encrypted.zip": "fables"},
            "fables",
        ),
        (
            # it prefers a password for a matching path
            "sub_dir/encrypted.zip",
            {"sub_dir/encrypted.zip": "fables", "encrypted.zip": "foobles"},
            "fables",
        ),
        (
            # right now we set to the best password, which will default to the
            # only given password even if the file is not a match
            "sub_dir/encrypted.zip",
            {"sub_dir/basic.zip": "fables"},
            "fables",
        ),
        (
            # the sub dir path matters in the match
            "sub_dir_1/encrypted.zip",
            {"sub_dir_1/encrypted.zip": "fables", "sub_dir_2/encrypted.zip": "foobles"},
            "fables",
        ),
        (
            # it will match on all extension patterns
            "encrypted.zip",
            {"*.zip": "fables", "*.xlsx": "foobles"},
            "fables",
        ),
        (
            # a variation on the test above
            "encrypted.xlsx",
            {"*.zip": "fables", "*.csv": "foobles"},
            "foobles",
        ),
        (
            # a more precise match spec will win
            "encrypted.zip",
            {"*.zip": "fables", "encrypted.zip": "foobles"},
            "foobles",
        ),
    ],
)
def test_it_assigns_the_right_password(name, passwords, expected_password):
    node = fables.FileNode(name=name, passwords=passwords)
    assert node.password == expected_password


def test_add_password_to_node():
    node = fables.FileNode(name="basic.zip", passwords={"basic.zip": "fables"})
    node.add_password(name="nested.zip", password="foobles")
    assert node.passwords == {"basic.zip": "fables", "nested.zip": "foobles"}


def test_node_str():
    node = fables.Xls(name="basic.xls", mimetype="application/vnd.ms-excel")
    assert str(node) == "Xls(name=basic.xls, mimetype=application/vnd.ms-excel)"

    node = fables.Directory(name="sub_dir", mimetype=None)
    assert str(node) == "Directory(name=sub_dir, mimetype=None)"


def test_mimetype_from_stream_for_empty_stream():
    mimetype = fables.mimetype_from_stream(None)
    assert mimetype is None

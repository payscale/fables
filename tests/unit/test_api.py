import io
import os

import pytest

from tests.context import fables


class MockOSStatResult:
    def __init__(self, size):
        self.st_size = size


@pytest.mark.parametrize(
    "name,size,expected_to_be_too_big",
    [("big_file", 1.1 * 1024 ** 3, True), ("small_file", 0.9 * 1024 ** 3, False)],
)
def test_check_file_size_detects_when_file_is_too_large(
    name, size, expected_to_be_too_big, monkeypatch
):
    def mock_stat(name):
        """Example (we are mocking the 'stat_result' object):
        >>> stat_result = os.stat('file.txt')
        >>> print(stat_result.st_size)
        """
        return MockOSStatResult(size)

    monkeypatch.setattr(os, "stat", mock_stat)

    too_big, _ = fables.api._check_file_size(name)
    assert too_big is expected_to_be_too_big


def test_detect_raises_a_value_error_when_file_is_too_large(monkeypatch):
    def mock_exists(*args):
        return True

    monkeypatch.setattr(os.path, "exists", mock_exists)

    file_size = 1.1 * 1024 ** 3

    def mock_stat(name):
        return MockOSStatResult(file_size)

    monkeypatch.setattr(os, "stat", mock_stat)

    with pytest.raises(ValueError) as e:
        fables.detect("file.csv")

    exception_message = str(e.value)
    assert "detect" in exception_message
    assert f"size={file_size} > fables.MAX_FILE_SIZE" in exception_message


@pytest.mark.parametrize(
    "size,expected_to_be_too_big", [(1.1 * 1024 ** 3, True), (0.9 * 1024 ** 3, False)]
)
def test_detect_detects_when_stream_is_too_large(
    size, expected_to_be_too_big, monkeypatch
):
    def mock_tell():
        return size

    stream = io.BytesIO(b"file bytes")
    monkeypatch.setattr(stream, "tell", mock_tell)

    too_big, _ = fables.api._check_stream_size(stream)
    assert too_big is expected_to_be_too_big


def test_detect_raises_a_value_error_when_stream_is_too_large(monkeypatch):
    stream_size = 1.1 * 1024 ** 3

    def mock_tell():
        return stream_size

    stream = io.BytesIO(b"file bytes")
    monkeypatch.setattr(stream, "tell", mock_tell)

    with pytest.raises(ValueError) as e:
        fables.detect(io=stream)

    exception_message = str(e.value)
    assert "detect" in exception_message
    assert f"size={stream_size} > fables.MAX_FILE_SIZE" in exception_message


def _it_raises_a_value_error_when_passwords_is_not_a_dict(callable):
    with pytest.raises(ValueError) as e:
        list(callable(io=io.BytesIO(b"file bytes"), passwords="fables"))

    exception_message = str(e.value)
    assert f"{callable.__name__}" in exception_message


def test_detect_raises_a_value_error_when_passwords_is_not_a_dict():
    _it_raises_a_value_error_when_passwords_is_not_a_dict(fables.detect)


def test_parse_raises_a_value_error_when_passwords_is_not_a_dict():
    _it_raises_a_value_error_when_passwords_is_not_a_dict(fables.parse)


def _it_raises_a_value_error_when_password_is_not_a_str(callable):
    with pytest.raises(ValueError) as e:
        list(callable(io=io.BytesIO(b"file bytes"), password={"filename": "fables"}))

    exception_message = str(e.value)
    assert f"{callable.__name__}" in exception_message


def test_detect_raises_a_value_error_when_password_is_not_a_str():
    _it_raises_a_value_error_when_password_is_not_a_str(fables.detect)


def test_parse_raises_a_value_error_when_password_is_not_a_str():
    _it_raises_a_value_error_when_password_is_not_a_str(fables.parse)


def test_parse_raises_value_error_when_no_io_or_tree_is_given():
    with pytest.raises(ValueError) as e:
        list(fables.parse(io=None, tree=None))

    exception_message = str(e.value)
    assert "parse" in exception_message
    assert "io" in exception_message
    assert "tree" in exception_message


def test_detect_accepts_a_stream_file_name():
    nameless_stream = io.BytesIO(b"fables")
    stream_file_name = "fables.txt"
    node = fables.detect(io=nameless_stream, stream_file_name=stream_file_name)
    assert node.stream.name == stream_file_name


def test_parse_accepts_a_stream_file_name():
    nameless_stream = io.BytesIO(b"a,b\n1,2\n3,4\n")
    stream_file_name = "fables.txt"
    parse_results = list(
        fables.parse(io=nameless_stream, stream_file_name=stream_file_name)
    )
    assert parse_results[0].tables[0].name == stream_file_name


def test_node_stream_property_returns_at_byte_0_after_detect():
    stream = io.BytesIO(b"a,b\n1,2\n3,4\n")
    node = fables.detect(stream)
    assert node._stream.tell() == 0
    with node.stream as node_stream:
        assert node_stream.tell() == 0


def test_node_stream_property_returns_at_byte_0_after_parse():
    stream = io.BytesIO(b"a,b\n1,2\n3,4\n")
    node = fables.detect(stream)
    for _ in fables.parse(tree=node):
        pass
    assert node._stream.tell() == 0
    with node.stream as node_stream:
        assert node_stream.tell() == 0

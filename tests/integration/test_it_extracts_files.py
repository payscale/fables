import io
import os

from tests.context import fables
from tests.integration.constants import DATA_DIR


def test_zip_children_nodes_have_file_name_for_named_stream():
    """
    basic.zip
        basic.csv
        basic.xlsx
    """
    zip_file = 'basic.zip'
    zip_path = os.path.join(DATA_DIR, zip_file)
    expected_children_names = {
        os.path.join(zip_file, 'basic.csv'),
        os.path.join(zip_file, 'basic.xlsx'),
    }

    with open(zip_path, 'rb') as zip_stream:
        tree = fables.detect(zip_stream)

        children_names = set()
        for child in tree.children:
            children_names.add(child.name)
        assert children_names == expected_children_names


def test_zip_children_nodes_have_file_name_for_nameless_stream():
    """
    basic.zip
        basic.csv
        basic.xlsx
    """
    zip_path = os.path.join(DATA_DIR, 'basic.zip')
    expected_children_names = {'basic.csv', 'basic.xlsx'}

    with open(zip_path, 'rb') as zip_stream:
        nameless_stream = io.BytesIO(zip_stream.read())
        nameless_stream.seek(0)

        tree = fables.detect(nameless_stream)

        children_names = set()
        for child in tree.children:
            children_names.add(child.name)
        assert children_names == expected_children_names

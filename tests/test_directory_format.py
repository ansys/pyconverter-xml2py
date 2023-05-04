import os

import ansys.dita.ast.directory_format as ff
import pytest


def test_xml_path(directory_path):
    assert os.path.abspath(os.path.expanduser(directory_path)) == ff.xml_path(directory_path)


def test_missing_xml_path():
    with pytest.raises(RuntimeError):
        ff.xml_path()


def test_get_path(directory_path):
    assert os.path.join(directory_path, "graphics") == ff.get_paths(directory_path)[0]
    assert os.path.join(directory_path, "links") == ff.get_paths(directory_path)[1]
    assert os.path.join(directory_path, "terms") == ff.get_paths(directory_path)[2]
    assert os.path.join(directory_path, "xml") == ff.get_paths(directory_path)[3]

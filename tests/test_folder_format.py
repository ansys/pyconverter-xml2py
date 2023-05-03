import os

import ansys.dita.ast.folder_format as ff
import pytest


@pytest.fixture
def folder_path(ghdir):
    folder_path = os.path.join(ghdir, "mapdl-cmd-doc")
    return folder_path


# ##########################################################+
# ##########################################################
# # To run the Unit Tests locally
# ##########################################################
# ##########################################################


# @pytest.fixture
# def folder_path():
#     return "D:/repos/pyansys/mapdl-cmd-doc-generalized"


# ##########################################################
# ##########################################################


def test_xml_path(folder_path):
    assert os.path.abspath(os.path.expanduser(folder_path)) == ff.xml_path(folder_path)


def test_missing_xml_path():
    with pytest.raises(RuntimeError):
        ff.xml_path()


def test_get_path(folder_path):
    assert os.path.join(folder_path, "graphics") == ff.get_paths(folder_path)[0]
    assert os.path.join(folder_path, "links") == ff.get_paths(folder_path)[1]
    assert os.path.join(folder_path, "terms") == ff.get_paths(folder_path)[2]
    assert os.path.join(folder_path, "xml") == ff.get_paths(folder_path)[3]

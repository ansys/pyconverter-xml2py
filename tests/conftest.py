import os

import pytest

import ansys.dita.ast.folder_format as ff
import ansys.dita.ast.load_xml_doc as lxd
import ansys.dita.ast.writer as wrt

pytest_plugins = ["pytester"]

# This is to run in the GH actions.
def pytest_addoption(parser):
    parser.addoption("--ghdir", action="store", default="./")


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    option_value = metafunc.config.option.ghdir
    if "ghdir" in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("ghdir", [option_value])


########################################################+
#########################################################
# To run the Unit Tests with GitHub actions
#########################################################
#########################################################


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


@pytest.fixture
def graph_path(folder_path):
    return ff.get_paths(folder_path)[0]


@pytest.fixture
def link_path(folder_path):
    return ff.get_paths(folder_path)[1]


@pytest.fixture
def term_path(folder_path):
    return ff.get_paths(folder_path)[2]


@pytest.fixture
def xml_path(folder_path):
    return ff.get_paths(folder_path)[3]


@pytest.fixture
def docu_global(term_path):
    return lxd.load_docu_global(term_path)


@pytest.fixture
def links(link_path):
    return lxd.load_links(link_path)


@pytest.fixture
def fcache(graph_path):
    return lxd.load_fcache(graph_path)


@pytest.fixture
def load_terms(term_path, docu_global, links, fcache):
    return lxd.load_terms(term_path, docu_global, links, fcache)


@pytest.fixture
def terms(load_terms):
    return load_terms[0]


@pytest.fixture
def version_variables(load_terms):
    return load_terms[1]


@pytest.fixture
def commands(folder_path):
    return wrt.convert(folder_path)

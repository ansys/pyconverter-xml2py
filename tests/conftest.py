import os

import ansys.dita.ast.directory_format as ff
import ansys.dita.ast.load_xml_doc as lxd
import ansys.dita.ast.writer as wrt
import pytest

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


@pytest.fixture
def directory_path(ghdir):
    import ansys.dita.ast as ast

    if os.environ.get("ON_CI", "").lower() == "true":
        directory_path = os.path.join(ghdir, "mapdl-cmd-doc")
    else:
        directory_path = os.path.abspath(ast.__file__)
    return directory_path


@pytest.fixture
def graph_path(directory_path):
    return ff.get_paths(directory_path)[0]


@pytest.fixture
def link_path(directory_path):
    return ff.get_paths(directory_path)[1]


@pytest.fixture
def term_path(directory_path):
    return ff.get_paths(directory_path)[2]


@pytest.fixture
def xml_path(directory_path):
    return ff.get_paths(directory_path)[3]


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
def commands(directory_path):
    return wrt.convert(directory_path)

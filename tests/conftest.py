# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
from pathlib import Path

from pyconverter.xml2py.custom_functions import CustomFunctions
import pyconverter.xml2py.directory_format as ff
import pyconverter.xml2py.load_xml_doc as lxd
from pyconverter.xml2py.utils.utils import get_comment_command_dict, get_config_data_value
import pyconverter.xml2py.writer as wrt
import pytest

pytest_plugins = ["pytester"]

# This is to run in the GH actions.
def pytest_addoption(parser):
    parser.addoption("--ghdir", action="store", default="./")


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    option_value = Path(metafunc.config.option.ghdir)
    if "ghdir" in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("ghdir", [option_value])


@pytest.fixture
def directory_path(ghdir):
    if os.environ.get("ON_CI", "").lower() == "true":
        directory_path = Path(ghdir) / "mapdl-cmd-doc"
    else:
        directory_path = Path.cwd().parent.parent / "ansys-internal" / "mapdl-cmd-doc"
        directory_path = directory_path.resolve()
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
def base_class_test_config(tmp_path):
    """
    Create a temporary config.yaml file for testing base class inheritance
    without using the general config.yaml file.
    
    Returns
    -------
    Path
        Path to the temporary config file with base class rules.
    """
    config_content = """
project_name: PyConverter-TestConfig

library_name_structured:
  - pyconverter
  - generatedcommands

base_class:
  rules:
    # Specific class gets a special base class (checked first)
    - pattern: "prep7/Meshing"
      module: "ansys.mapdl.core._commands.prep"
      class_name: "PrepBase"
    
    # Specific module inheritance
    - pattern: "apdl/*"
      module: "ansys.mapdl.core._commands.apdl"
      class_name: "APDLBase"
    
    # Make all classes inherit from BaseCommandClass (fallback)
    - pattern: "*"
      module: "ansys.mapdl.core._commands"
      class_name: "CommandsBase"
"""
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(config_content)
    return config_file


@pytest.fixture
def base_class_empty_config(tmp_path):
    """
    Create a temporary config.yaml file with no base class rules
    for testing the default behavior.
    
    Returns
    -------
    Path
        Path to the temporary config file without base class rules.
    """
    config_content = """
project_name: PyConverter-TestConfig

library_name_structured:
  - pyconverter
  - generatedcommands
"""
    config_file = tmp_path / "test_config_no_base.yaml"
    config_file.write_text(config_content)
    return config_file


@pytest.fixture
def command_map(directory_path):
    return wrt.convert(directory_path)[0]


@pytest.fixture
def name_map(directory_path):
    return wrt.convert(directory_path)[1]


@pytest.fixture
def cwd():
    return Path.cwd()


@pytest.fixture
def path_custom_functions(cwd):
    return cwd / "tests" / "customized_functions"


@pytest.fixture
def custom_functions(path_custom_functions):
    return CustomFunctions(path_custom_functions)


@pytest.fixture
def config_path(cwd):
    return cwd / "config.yaml"


@pytest.fixture
def image_folder_path(cwd):
    return get_config_data_value(cwd / "config.yaml", "image_folder_path")


@pytest.fixture
def library_name_structured(config_path):
    lib_structure = get_config_data_value(config_path, "library_name_structured")
    subfolders = get_config_data_value(config_path, "subfolders")
    if subfolders is not None:
        lib_structure.extend(get_config_data_value(config_path, "subfolders"))
    return lib_structure


@pytest.fixture
def package_structure(command_map, name_map, directory_path, cwd, path_custom_functions):
    return wrt.write_source(command_map, name_map, directory_path, cwd, path_custom_functions)


@pytest.fixture
def comment_command_dict(config_path):
    return get_comment_command_dict(config_path)

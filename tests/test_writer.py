# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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
import shutil

import pyconverter.xml2py.writer as wrt
import pytest


def test_convert(commands, cmd_map, custom_functions):
    assert commands["/XFRM"].name == "/XFRM"
    assert (
        "Original command: WRITE\n\nShort Description:\nWrites the radiation matrix file.\n\nFunction signature:\nWRITE,"  # noqa : E501
        in commands["WRITE"].__repr__()
    )
    assert (
        commands["E"].py_source(custom_functions, cmd_map)
        == '    command = f"E,{i},{j},{k},{l},{m},{n},{o},{p}"\n    return self.run(command, **kwargs)\n'  # noqa : E501
    )
    assert 'def zoom(self, wn="", lab="", x1="", y1="", x2="", y2="", **kwargs):\n    r"""Zooms a region of a display window.\n\n' in commands[  # noqa : E501
        "/ZOOM"
    ].to_python(
        cmd_map, custom_functions
    )
    assert "import re" in commands["K"].to_python(cmd_map, custom_functions)


def test_copy_package(cwd):
    new_package_path = os.path.join(cwd, "tmp_directory")
    if os.path.isdir(new_package_path):
        shutil.rmtree(new_package_path)
    os.makedirs(new_package_path)
    template_path = os.path.join(cwd, "_package")
    wrt.copy_package(template_path, new_package_path)
    assert os.path.isdir(new_package_path) is True
    assert os.path.isdir(os.path.join(new_package_path, "doc")) is True
    assert os.path.isfile(os.path.join(new_package_path, "LICENSE")) is True
    assert os.path.isdir(os.path.join(new_package_path, "doc", "source", "_templates")) is True
    assert (
        os.path.isfile(os.path.join(new_package_path, "doc", "source", "_templates", "base.rst"))
        is True
    )
    shutil.rmtree(new_package_path)


@pytest.fixture
def cwd():
    return os.getcwd()


@pytest.fixture
def package_path(cwd):
    return os.path.join(cwd, "package")


def test_write_source_with_custom_functions(
    commands, cmd_map, path_custom_functions, cwd, directory_path, package_path
):
    cmd_path = wrt.write_source(commands, cmd_map, directory_path, cwd, path_custom_functions)
    assert cmd_path == os.path.join(package_path, wrt.GENERATED_SRC_CODE)
    assert os.path.isfile(os.path.join(cmd_path, "acel.py"))
    assert os.path.isdir(os.path.join(package_path, "doc", "source", "images"))
    assert os.path.isfile(os.path.join(package_path, "doc", "source", "images", "gcmdrsymm1.png"))


def test_write_source_no_custom_function(commands, cmd_map, directory_path, cwd, package_path):
    cmd_path = wrt.write_source(commands, cmd_map, directory_path, cwd)
    assert cmd_path == os.path.join(package_path, wrt.GENERATED_SRC_CODE)
    assert os.path.isfile(os.path.join(cmd_path, "acel.py"))
    assert os.path.isdir(os.path.join(package_path, "doc", "source", "images"))
    assert os.path.isfile(os.path.join(package_path, "doc", "source", "images", "gcmdrsymm1.png"))


def test_write_docs(commands, cmd_map, package_path):
    doc_src = wrt.write_docs(commands, cmd_map, package_path)
    file = open(doc_src, "r")
    content = file.read()
    file.close()
    assert "Autosummary" in content
    assert "agen" in content

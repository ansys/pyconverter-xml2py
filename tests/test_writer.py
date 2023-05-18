import os
import shutil

import pydita.ast.writer as wrt
import pytest


def test_convert(commands, custom_functions):
    assert commands["/XFRM"].name == "/XFRM"
    assert (
        "APDL Command: WRITE\n\nShort Description:\nWrites the radiation matrix file.\n\nFunction signature:\nWRITE,"  # noqa : E501
        in commands["WRITE"].__repr__()
    )
    assert (
        commands["E"].py_source(custom_functions)
        == '    command = f"E,{i},{j},{k},{l},{m},{n},{o},{p}"\n    return self.run(command, **kwargs)\n'  # noqa : E501
    )
    assert 'def zoom(self, wn="", lab="", x1="", y1="", x2="", y2="", **kwargs):\n    r"""Zooms a region of a display window.\n\n' in commands[  # noqa : E501
        "/ZOOM"
    ].to_python(
        custom_functions
    )
    assert "import re" in commands["K"].to_python(custom_functions)


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


def test_write_source(commands, cwd, directory_path, package_path):
    cmd_path = wrt.write_source(commands, directory_path, cwd)
    assert cmd_path == os.path.join(package_path, wrt.generated_src_code)
    assert os.path.isfile(os.path.join(cmd_path, "acel.py"))
    assert os.path.isdir(os.path.join(package_path, "doc", "source", "images"))
    assert os.path.isfile(os.path.join(package_path, "doc", "source", "images", "gcmdrsymm1.png"))


def test_write_docs(commands):
    cwd = os.getcwd()
    doc_src = wrt.write_docs(commands, cwd)
    file = open(doc_src, "r")
    content = file.read()
    file.close()
    assert "Autosummary" in content
    assert "agen" in content

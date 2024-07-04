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

"""Command Line Interface for PyConverter-XML2Py."""

import os

import click
from pyconverter.xml2py import __version__, download
from pyconverter.xml2py import writer as wr
from pyconverter.xml2py import utils


def create_package(xml_path=None, functions_path=None, target_path=None, template_path=None, json_structure_path=None):
    """Create Python package based on a XML documentation.

    Parameters
    ----------
    xml_path: str
        Path to the directory that contains the XML documentation to convert.

    functions_path: str, optional
        Path to the directory that contains the functions that need to be customized.
        The default value is None.

    target_path: str, optional
        Path to the directory where you want to create the autogenerated package.
        The default value is the current working directory.

    template_path: str, optional
        Path for the template to use. If no path is provided, the default template is used.
        The default value is the ``_package`` directory accessible in the
        `PyConverter-XML2Py GitHub repository <https://github.com/ansys/pyconverter-xml2py/tree/main/_package>`_.

    json_structure_path: str, optional
        Path to the JSON file that contains the structure map of the package.
        The structure map is a dictionary with the following format: ``{'module_name': [{'class_name': python_names_list}]}".
        The default value is ``None``.
    """  # noqa : E501
    if xml_path is None:
        xml_path = os.environ.get("XML_PATH")
    if xml_path is None:
        raise RuntimeError(
            "Missing the XML documentation path. Specify this with either xml_path or set the XML_PATH environment variable"  # noqa : E501
        )
    else:
        xml_path = os.path.abspath(os.path.expanduser(xml_path))
        if not os.path.isdir(xml_path):
            raise FileExistsError(
                "Please, enter a valid directory path that contains the XML documentation to convert."  # noqa : E501
            )

    if functions_path is None:
        print(
            "No customized functions path was entered. The default code generation will be applied to all the commands.",  # noqa : E501
            "You can specify the customized functions by adding a path to the --func-path argument.",  # noqa : E501
        )

    else:
        functions_path = os.path.abspath(os.path.expanduser(functions_path))
        if not os.path.isdir(functions_path):
            raise FileExistsError(
                "Please, enter a valid directory path that contains the functions that need to be customized."  # noqa : E501
            )

    if target_path is None:
        target_path = os.getcwd()

    else:
        os.makedirs(target_path, exist_ok=True)
        print(f"The autogenerated package will be saved in {target_path}.")

    if template_path is None:
        if not os.path.isdir(os.path.join(os.getcwd(), "_package")):
            download.download_template()

    if json_structure_path is not None:
        structure_map = utils.parse_package_structure(json_structure_path)
    else:
        structure_map = None
    command_map, name_map, *_ = wr.convert(xml_path)
    module_names = wr.write_source(command_map, name_map, xml_path, target_path, functions_path, structure_map=structure_map)
    package_path = os.path.join(target_path, "package")
    wr.write_docs(name_map, package_path, module_names, structure_map)


@click.group()
def main():
    """A Python wrapper to convert XML documentation into Python source code
    with its related Sphinx documentation."""
    pass


@main.command()
def version():
    """Display current version."""
    print(f"pyconverter.xml2py {__version__}")


@main.command()
@click.option(
    "-x",
    "--xml-path",
    type=click.Path(exists=True),
    help="Path to the directory that contains the XML documentation to convert.",
)
@click.option(
    "-f",
    "--func-path",
    type=click.Path(exists=True),
    help="Path to the directory that contains the functions that need to be customized.",
)
@click.option(
    "-p",
    "--targ-path",
    type=click.Path(),
    help="Path to the directory where you want the autogenerated package to be created.",
)
@click.option(
    "-t",
    "--template-path",
    type=click.Path(),
    help="Path for the template to use. If no path is provided, the default template is used.",
)
@click.option(
    "-j",
    "--json-path",
    type=click.Path(),
    help="Path to the JSON file that contains the structure map of the package.",
)
def package(xml_path, func_path, targ_path, template_path, json_path):
    """Create a Python package from your XML documentation."""
    create_package(xml_path, func_path, targ_path, template_path, json_path)

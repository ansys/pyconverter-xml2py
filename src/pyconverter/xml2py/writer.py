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

import glob
import os
import shutil

from pyconverter.xml2py import ast_tree as ast
from pyconverter.xml2py import load_xml_doc as load
from pyconverter.xml2py.custom_functions import CustomFunctions
from pyconverter.xml2py.directory_format import get_paths
from pyconverter.xml2py.download import download_template
from pyconverter.xml2py.utils import create_name_map, get_config_data_value, import_handler
import regex as re
from tqdm import tqdm

# common statements used within the docs to avoid duplication
CONST = {
    "Dtl?": "",
    "Caret?": "",
    "Caret1?": "",
    "Caret 40?": "",
    '``"``': "``",
}

# XML commands to skip
SKIP_XML = {"*IF", "*ELSE", "C***", "*RETURN", "*DEL"}
SKIP_PYCOMMAND = {"if", "else", "c", "return", "del"}


def convert(directory_path):
    """
    Convert an XML directory into an RST dictionary.

    Parameters
    ----------
    directory_path : str
        Path to the directory containing the XML files to convert.

    Returns
    -------
    dict
        Dictionary with the following format: ``{"command_name": command_object}``.

    dict
        Dictionary with the following format: ``{"initial_command_name": "python_name"}``.

    dict
        Dictionary with the following format: ``{"link_name": link_object}``.

    Autogenerateddirectory
        Object containing the version variables of the XML documentation.
    """

    graph_path, link_path, term_path, xml_path = get_paths(directory_path)
    links = load.load_links(link_path)
    fcache = load.load_fcache(graph_path)
    docu_global = load.load_docu_global(term_path)
    terms, version_variables = load.load_terms(term_path, docu_global, links, fcache)

    def load_commands(
        xml_path,
        meta_only=False,
    ):
        """Scrape the command information from the XML command reference.

        Parameters
        ----------
        xml_path : str
            Path to the directory containing the XML files to convert.

        Examples
        --------
        >>> from convert import load_commands
        >>> commands = load_commands(
        ...     '/home/user/source/xml-cmd-doc/docu_files/ans_cmd/'
        ... )

        Returns
        -------
        dict
            Dictionary with the following format: ``{"command_name": command_object}``.

        """
        if not os.path.isdir(xml_path):
            raise FileNotFoundError(f'Invalid path "{xml_path}"')

        filenames = list(glob.glob(os.path.join(xml_path, "**", "*.xml"), recursive=True))

        if meta_only:
            desc = "Loading command metadata"
        else:
            desc = "Loading commands"

        xml_commands = []
        for filename in tqdm(filenames, desc=desc):
            try:
                command = ast.XMLCommand(
                    filename,
                    terms,
                    docu_global,
                    version_variables,
                    links,
                    fcache,
                    meta_only=meta_only,
                )
                xml_commands.append(command)
                if meta_only == False:
                    refnamediv = command.get_children_by_type("Refnamediv")[0]
                    ref = str(refnamediv.get_children_by_type("Refclass")[0])
                    try:
                        ref = re.findall(r"(?<=&)(.*?)(?=;)", ref)[0]
                        if ref == "xtycadimport":
                            continue  # CAD imports need to be handdled differently
                        command.group = terms[ref]
                    except IndexError:
                        classname = re.findall(r"(.*?)(?=:)", ref)
                        if "" in classname:
                            classname.remove("")
                        if len(classname) > 1:
                            typename = re.findall(r"(?<=:)(.*?)(?=[A-Z][A-Z])", classname[1])[
                                0
                            ]  # the function will only appear in one module (example with CECYC)
                        else:
                            typename = re.findall(r"(?<=:)(.*)", ref)[0]
                        command_group = [classname[0], typename]
                        command.group = command_group
                        command.is_archived = True
            except RuntimeError:
                continue

        return {cmd.name: cmd for cmd in xml_commands}

    command_map_meta = load_commands(
        os.path.expanduser(xml_path),
        meta_only=True,
    )
    meta_command = command_map_meta.keys()

    # create command mapping between the ansys command name and the pycommand method
    # remove the start and slash whenever possible, for example, /GCOLUMN can simply
    # be gcolumn since it's the only command, but VGET and *VGET must be vget and star_vget

    name_map = create_name_map(meta_command, "config.yaml")

    # TODO : accept conversion of a single command

    # convert a single command
    # if command is not None:
    #     if command not in command_meta:
    #         raise ValueError(f"Invalid command {command}")
    #     fname = command_meta[command].xml_filename
    #     cmd = ast.XMLCommand(os.path.expanduser(fname), )
    #     commands = {to_py_name(cmd.name): cmd}
    # else:  # convert all commands

    command_map = load_commands(xml_path)

    return command_map, name_map, links, version_variables


def copy_template_package(template_path, new_package_path, clean=False, include_hidden=False):
    """
    Add files and directory from a template directory path to a new path.

    Parameters
    ----------
    template_path : str
        Path containing the directory to copy.

    new_package_path : str
        Path containing the directory where the new files and directorys are to be added.

    clean : bool, optional
        Whether the directories in the path for the new package must be cleared before adding
        new files. The default is ``False``.

    include_hidden : bool, optional
        Whether to handle hidden files automatically when the Python version is 3.11 or later.
        The default is ``False``.

    Returns
    -------
    str
        Path containing the source files of the created
        ``xml-commands`` package.

    """
    # For Python version >= 3.11, glob.glob() handles it if include_hidden=True.
    if include_hidden is True:
        try:  # Python 3.11 or later
            filename_list = glob.glob(
                os.path.join(template_path, "*"), recursive=True, include_hidden=True
            )
        except:
            filename_list = glob.glob(os.path.join(template_path, "*"), recursive=True)
    else:
        filename_list = glob.glob(os.path.join(template_path, "*"), recursive=True)

    for filename in filename_list:
        split_name_dir = filename.split(os.path.sep)
        new_path_dir = os.path.join(new_package_path, split_name_dir[-1])

        if os.path.isdir(filename):
            if not os.path.isdir(new_path_dir):
                os.makedirs(new_path_dir, exist_ok=True)
            elif os.path.isdir(new_path_dir) and clean:
                shutil.rmtree(new_path_dir)
                os.makedirs(new_path_dir)
            copy_template_package(filename, new_path_dir, clean)

        else:
            shutil.copy(filename, new_package_path)

    if include_hidden is False:
        # .vale.ini and .gitignore are hidden files.
        vale_path = ["doc", ".vale.ini"]
        gitignore_path = ["doc", "styles", ".gitignore"]
        hidden_path = [vale_path, gitignore_path]
        for hpath in hidden_path:
            hidden_template = os.path.join(template_path, *hpath)
            hidden_new_path = os.path.join(new_package_path, *hpath)
            if os.path.isfile(hidden_template) and not os.path.isfile(hidden_new_path):
                shutil.copy(hidden_template, hidden_new_path)


def write_global__init__file(library_path, module_name_list):
    """
    Write the __init__.py file for the package generated.

    Parameters
    ----------
    library_path : str
        Path to the directory containing the generated package.

    name_map : dict
        Dictionary with the following format: ``{"initial_command_name": "python_name"}``.

    command_map : dict
        Dictionary with the following format: ``{"initial_command_name": command_object}``.

    structure_map : dict, optional
        Dictionary with the following format:
        ``{'module_name': [{'class_name': python_names_list}]}``.
        The default value is ``None``.
    """
    mod_file = os.path.join(library_path, "__init__.py")
    # TODO: needs to be modified due to the new structure

    with open(mod_file, "w") as fid:
        fid.write(f"from . import (\n")
        for dir in os.listdir(library_path):
            if os.path.isdir(os.path.join(library_path, dir)):
                fid.write(f"    {dir},\n")
        fid.write(")\n\n")
        fid.write("try:\n")
        fid.write("    import importlib.metadata as importlib_metadata\n")
        fid.write("except ModuleNotFoundError:\n")
        fid.write("    import importlib_metadata\n\n")
        fid.write("__version__ = importlib_metadata.version(__name__.replace('.', '-'))\n")
        fid.write('"""PyConverter-GeneratedCommands version."""\n')
    fid.close()


def write__init__file(library_path):

    for dir in os.listdir(library_path):
        if os.path.isdir(os.path.join(library_path, dir)):
            listdir = os.listdir(os.path.join(library_path, dir))
            if len(listdir) > 0:
                with open(os.path.join(library_path, dir, "__init__.py"), "w") as fid:
                    fid.write(f"from . import (\n")
                    for file in listdir:
                        if file.endswith(".py"):
                            fid.write(f"    {file[:-3]},\n")
                    fid.write(")\n")
                    fid.close()


def get_library_path(new_package_path, config_path):
    """
    Return the desired library path with the following format:
    ``new_package_path/library_structure``.

    For instance, if ``library_name_structured`` in the ``config.yaml`` file is
    ``["pyconverter", "generatedcommands"]``, the function will return
    ``new_package_path/pyconverter/generatedcommands``.

    Parameters
    ----------
    new_package_path : str
        Path to the new package directory.
    config_path : str
        Path to the configuration file.

    Returns
    -------
    str
        Path to the desired library structure.
    """
    library_name = get_config_data_value(config_path, "library_name_structured")
    if not "src" in library_name:
        library_name.insert(0, "src")
    library_name_str = "/".join(library_name)
    return os.path.join(new_package_path, library_name_str)


def write_source(
    command_map,
    name_map,
    xml_doc_path,
    target_path,
    path_custom_functions=None,
    template_path=None,
    config_path="config.yaml",
    clean=True,
    structured=True,
):
    """Write out XML commands as Python source files.

    Parameters
    ----------
    command_map : dict
        Dictionary with the following format: ``{"initial_command_name": command_obj}``.

    name_map : dict
        Dictionary with the following format: ``{"initial_command_name": "python_name"}``.

    xml_doc_path : str
        Path containing the XML directory to convert.

    target_path : str
        Path to generate the new package to.

    path_custom_functions : str, optional
        Path containing the customized functions. The default is ``None``.

    template_path : str, optional
        Path for the template to use. If no path is provided, the default template is used.

    config_path : str, optional
        Path to the configuration file. The default is ``config.yaml``.

    structure_map : dict, optional
        Dictionary with the following format:
        ``{'module_name': [{'class_name': python_names_list}]}``.
        The default value is ``None``.

    clean : bool, optional
        Whether the directories in the new package path must be cleared before adding
        new files. The default value is ``True``.

    Returns
    -------
    list
        List of module names created.

    dict
        Dictionary with the following format:
        ``{'python_module_name': [{'python_class_name': python_names_list}]}``.
    """

    if path_custom_functions is not None:
        custom_functions = CustomFunctions(path_custom_functions)
    else:
        custom_functions = None

    if template_path is None:
        print("The default template will be used to create the new package.")
        template_path = os.path.join(os.getcwd(), "_package")
        if not os.path.isdir(template_path):
            download_template()

    new_package_name = get_config_data_value(config_path, "new_package_name")
    new_package_path = os.path.join(target_path, new_package_name)

    if clean:
        if os.path.isdir(new_package_path):
            shutil.rmtree(new_package_path)

    library_path = get_library_path(new_package_path, config_path)

    if not os.path.isdir(library_path):
        os.makedirs(library_path)

    module_name_list = []

    if structured == False:
        package_structure = None
        for initial_command_name, command_obj in tqdm(command_map.items(), desc="Writing commands"):
            if initial_command_name in SKIP_XML:
                continue
            python_name = name_map[initial_command_name]
            module_name_list.append(python_name)
            path = os.path.join(library_path, f"{python_name}.py")
            with open(path, "w", encoding="utf-8") as fid:
                python_method = command_obj.to_python(custom_functions)
                fid.write(f"{python_method}\n")

            try:
                exec(command_obj.to_python(custom_functions))
            except:
                raise RuntimeError(f"Failed to execute {python_name}.py") from None

    else:
        import subprocess

        package_structure = {}
        all_commands = []
        specific_classes = get_config_data_value(config_path, "specific_classes")

        for command in command_map.values():
            if command.name in SKIP_XML or command.group is None:
                continue
            initial_module_name, initial_class_name = command.group
            initial_module_name = initial_module_name.replace("/", "")
            module_name = initial_module_name.replace(" ", "_").lower()
            module_path = os.path.join(library_path, module_name)
            if not os.path.isdir(module_path):
                os.makedirs(module_path)
                package_structure[module_name] = {}
            if initial_class_name in specific_classes.keys():
                initial_class_name = specific_classes[initial_class_name]
            class_name = initial_class_name.title().replace(" ", "").replace("/", "")
            file_name = initial_class_name.replace(" ", "_").replace("/", "_").lower()
            if file_name == "":
                pass

            file_path = os.path.join(module_path, f"{file_name}.py")
            if not os.path.isfile(file_path):
                class_structure = []
                with open(file_path, "w", encoding="utf-8") as fid:
                    fid.write(f"class {class_name}:\n")
            else:
                class_structure = package_structure[module_name][file_name][1]
            class_structure.append(command.py_name)

            package_structure[module_name][file_name] = [class_name, class_structure]
            with open(file_path, "a", encoding="utf-8") as fid:
                python_method = command.to_python(custom_functions, prefix="    ")
                # check if there are any imports before the function definition.
                str_before_def = re.findall(r"[\s\S]*?(?=def)", python_method)[0]
                output = re.findall(r"((import|from) [^\n]*)", str_before_def)
                if len(output) == 0:
                    fid.write(f"{python_method}\n")
                    fid.close()
                else:
                    fid.close()
                    import_handler(file_path, python_method, output)

            all_commands.append(command.name)
        try:
            subprocess.run(["python", str(file_path)])
        except Exception as e:
            raise RuntimeError(f"Failed to execute '{python_method}' from '{file_path}'.") from e

        # for module_name, class_map in tqdm(structure_map.items(), desc="Writing commands..."):
        #     module_name = module_name.replace(" ", "_").lower()
        #     module_path = os.path.join(library_path, module_name)
        #     if not os.path.isdir(module_path):
        #         os.makedirs(module_path)
        #     module_name_list.append(module_name)
        #     class_structure = {}
        #     for initial_class_name, method_list in class_map.items():
        #         additional_imports = None
        #         if initial_class_name in specific_classes.keys():
        #             specific_class_dict = specific_classes[initial_class_name]
        #             class_name = specific_class_dict["class_name"]
        #             file_name = specific_class_dict["file_name"]
        #             file_path = os.path.join(module_path, f"{file_name}.py")
        #             if "additional_imports" in specific_class_dict.keys():
        #                 additional_imports = specific_class_dict["additional_imports"]
        #         else:
        #             class_name = initial_class_name.title().replace(" ", "").replace("/","")
        #             file_name = initial_class_name.replace(" ", "_").replace("/","_").lower()
        #             file_path = os.path.join(module_path, f"{file_name}.py")
        #         with open(file_path, "w", encoding="utf-8") as fid:
        #             if additional_imports is not None:
        #                 library_imports = additional_imports["library_imports"]
        #                 for library_import in library_imports:
        #                     fid.write(f"{library_import}\n")
        #                 fid.write("\n")
        #                 class_name_with_parent = additional_imports["class_name_with_parent"]
        #                 fid.write(f"class {class_name_with_parent}:\n")
        #             else:
        #                 fid.write(f"class {class_name}:\n")
        #             methods_structure = []
        #             for initial_command_name in method_list:
        #                 if initial_command_name in SKIP_XML:
        #                     continue
        #                 command_obj = command_map[initial_command_name]
        #                 python_method = command_obj.to_python(custom_functions, prefix='    ')
        #                 methods_structure.append(name_map[initial_command_name])
        #                 all_commands.append(initial_command_name)
        #                 fid.write(f"{python_method}\n")
        #         fid.close()
        #         try:
        #             subprocess.run(["python", str(file_path)])
        #         except:
        #             print(python_method)
        #             raise RuntimeError(f"Failed to execute {file_path}") from None

        #         class_structure[file_name] = [class_name, methods_structure]
        #     package_structure[module_name] = class_structure

    for command_name in name_map.keys():
        if command_name not in all_commands:
            print(f"{command_name} is not in the structure map")

    write_global__init__file(library_path, module_name_list)
    write__init__file(library_path)

    print(f"Commands written to {library_path}")

    # copy package files to the package directory
    copy_template_package(template_path, new_package_path, clean)
    graph_path = get_paths(xml_doc_path)[0]
    shutil.copytree(graph_path, os.path.join(new_package_path, "doc", "source", "images"))
    return package_structure


def write_docs(package_path, package_structure=None, config_path="config.yaml"):
    """Output to the autogenerated ``package`` directory.

    Parameters
    ----------
    name_map : dict
        Dictionary with the following format: ``{"initial_command_name": "python_name"}``.

    package_path : str
        Path to the new package folder.

    module_name_list : list
        List of module names created.

    package_structure :
        Dictionary with the following format:
        ``{'python_module_name': [{'python_class_name': python_names_list}]}``.

    Returns
    -------
    str
        Path to the new document page.

    """
    library_name = get_config_data_value(config_path, "library_name_structured")
    if library_name[0] == "src":
        library_name.pop(0)
    library_name = ".".join(library_name)

    doc_package_path = os.path.join(package_path, "doc/source")
    if not os.path.isdir(doc_package_path):
        os.makedirs(doc_package_path)

    doc_src = os.path.join(doc_package_path, "docs.rst")
    with open(doc_src, "w") as fid:
        fid.write(
            """
API documentation
==================

.. toctree::
   :maxdepth: 2
   :hidden:\n\n
"""
        )
        for module_name in package_structure.keys():
            fid.write(f"   {module_name}/index.rst\n")

    if package_structure is not None:
        for module_folder_name, class_map in tqdm(
            package_structure.items(), desc="Writing docs..."
        ):
            module_title = module_folder_name.replace("_", " ").capitalize()
            module_folder = os.path.join(doc_package_path, f"{module_folder_name}")
            if not os.path.isdir(module_folder):
                os.makedirs(module_folder)
            module_file = os.path.join(module_folder, f"index.rst")
            with open(module_file, "w") as fid:
                fid.write(f".. _ref_{module_folder_name}:\n\n")
                fid.write(f"{module_title}\n")
                fid.write("=" * len(module_title) + "\n\n")
                fid.write(f".. toctree::\n")
                fid.write(f"   :maxdepth: 2\n")
                fid.write(f"   :hidden:\n\n")
                for class_file_name in class_map.keys():
                    fid.write(f"   {class_file_name}\n")
            for class_file_name, (class_name, method_list)  in class_map.items():
                class_file = os.path.join(module_folder, f"{class_file_name}.rst")
                with open(class_file, "w") as fid:
                    fid.write(f".. _ref_{class_file_name}:\n\n")
                    fid.write(f"{class_name}\n")
                    fid.write("=" * len(class_name) + "\n\n")
                    fid.write(
                        f".. currentmodule:: {library_name}.{module_folder_name}.{class_file_name}\n\n"  # noqa : E501
                    )
                    fid.write(
                        f".. autoclass:: {library_name}.{module_folder_name}.{class_file_name}.{class_name}\n\n"  # noqa : E501
                    )
                    fid.write(".. autosummary::\n")
                    fid.write("   :template: base.rst\n")
                    fid.write("   :toctree: _autosummary\n\n")
                    for python_command_name in method_list:
                        fid.write(f"   {class_name}.{python_command_name}\n")

    return doc_src

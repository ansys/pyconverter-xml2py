# Copyright (c) 2023 ANSYS, Inc. All rights reserved.

import glob
import os
import shutil

from pyconverter.xml2py import ast_tree as ast
from pyconverter.xml2py import load_xml_doc as load
from pyconverter.xml2py.custom_functions import CustomFunctions
from pyconverter.xml2py.directory_format import get_paths
from tqdm import tqdm

RULES = {"/": "slash", "*": "star"}

GENERATED_SRC_CODE = os.path.join("src", "pyconverter", "generatedcommands")

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


def convert(directory_path, command=None):
    """Convert an XML directory into an RST dictionary."""

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
                xml_commands.append(
                    ast.XMLCommand(
                        filename,
                        terms,
                        docu_global,
                        version_variables,
                        links,
                        fcache,
                        meta_only=meta_only,
                    )
                )
            except RuntimeError:
                continue

        return {cmd.name: cmd for cmd in xml_commands}

    command_meta = load_commands(
        os.path.expanduser(xml_path),
        meta_only=True,
    )
    command_names = command_meta.keys()

    # create command mapping between the ansys command name and the pycommand method
    # remove the start and slash whenever possible, for example, /GCOLUMN can simply
    # be gcolumn since it's the only command, but VGET and *VGET must be vget and star_vget

    # convert all to flat and determine number of occurances
    proc_names = []
    for cmd_name in command_names:
        cmd_name = cmd_name.lower()
        if not cmd_name[0].isalnum():
            cmd_name = cmd_name[1:]
        proc_names.append(cmd_name)

    # reserved command mapping
    COMMAND_MAPPING = {"*DEL": "stardel"}

    # map command to pycommand function
    cmd_map = {}

    # second pass for each name
    for ans_name in command_names:
        if ans_name in COMMAND_MAPPING:
            py_name = COMMAND_MAPPING[ans_name]
        else:
            lower_name = ans_name.lower()
            if not lower_name[0].isalnum():
                alpha_name = lower_name[1:]
            else:
                alpha_name = lower_name

            if proc_names.count(alpha_name) != 1:
                if RULES:
                    py_name = lower_name
                    for rule_name, rule in RULES.items():
                        py_name = py_name.replace(rule_name, rule)
                    if py_name == lower_name and not py_name[0].isalnum():
                        raise ValueError(
                            f"Additional rules need to be defined. The {ans_name} function name is in conflict with another function."  # noqa : E501
                        )
                else:
                    raise ValueError(
                        "Some functions have identical names. You need to provide RULES."
                    )

            else:
                py_name = alpha_name

        cmd_map[ans_name] = py_name

    # TODO : accept conversion of a single command

    # convert a single command
    # if command is not None:
    #     if command not in command_meta:
    #         raise ValueError(f"Invalid command {command}")
    #     fname = command_meta[command].xml_filename
    #     cmd = ast.XMLCommand(os.path.expanduser(fname), )
    #     commands = {to_py_name(cmd.name): cmd}
    # else:  # convert all commands

    commands = load_commands(xml_path)

    return commands, cmd_map, links, version_variables


def copy_package(template_path, new_package_path, clean=False, include_hidden=False):
    """Add files and directory from a template directory path to a new path.

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
        filename_list = glob.glob(
            os.path.join(template_path, "*"), recursive=True, include_hidden=True
        )

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
            copy_package(filename, new_path_dir, clean)

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


def write_source(
    commands,
    cmd_map,
    xml_doc_path,
    template_path,
    path_custom_functions=None,
    new_package_path=None,
    clean=True,
):
    """Write out XML commands as Python source files.

    Parameters
    ----------
    commands : list[XMLCommand]
        List of XML commands

    cmd_map : dict
        Dictionary with this format: ``{"command_name": "python_name"}``.

    xml_doc_path : str
        Path containing the XML directory to convert.

    template_path : str
        Path containing the ``_package`` directory.

    path_custom_functions : str, optional
        Path containing the customized functions. The default is ``None``.

    new_package_path : str, optional
        Path to copy the ``_package`` directory to. The default is ``./package``.

    clean : bool, optional
        Whether the directories in the new package path must be cleared before adding
        new files. The default is ``True``.

    Returns
    -------
    str
        Path containing the source files of the created
        ``xml-commands`` package.

    """
    _package_path = os.path.join(template_path, "_package")
    if path_custom_functions is not None:
        custom_functions = CustomFunctions(path_custom_functions)
    else:
        custom_functions = None

    if not os.path.isdir(_package_path):
        raise FileNotFoundError(
            f"Unable to locate the package templates path at '{_package_path}'. "
            f"Expected the _package directory in '{path}'."
        )

    if new_package_path is None:
        new_package_path = os.path.join(template_path, "package")

    if clean:
        if os.path.isdir(new_package_path):
            shutil.rmtree(new_package_path)

    cmd_path = os.path.join(new_package_path, GENERATED_SRC_CODE)
    if not os.path.isdir(cmd_path):
        os.makedirs(cmd_path)

    for ans_name, cmd_obj in tqdm(commands.items(), desc="Writing commands"):
        if ans_name in SKIP_XML:
            continue
        cmd_name = cmd_map[ans_name]
        path = os.path.join(cmd_path, f"{cmd_name}.py")
        with open(path, "w", encoding="utf-8") as fid:
            fid.write(cmd_obj.to_python(cmd_map, custom_functions))

        try:
            exec(cmd_obj.to_python(cmd_map, custom_functions))
        except:
            raise RuntimeError(f"Failed to execute {cmd_name}.py") from None

    mod_file = os.path.join(cmd_path, "__init__.py")
    with open(mod_file, "w") as fid:
        for ans_name in commands:
            if ans_name in SKIP_XML:
                continue
            cmd_name = cmd_map[ans_name]
            fid.write(f"from .{cmd_name} import *\n")
        fid.write("try:\n")
        fid.write("    import importlib.metadata as importlib_metadata\n")
        fid.write("except ModuleNotFoundError:\n")
        fid.write("    import importlib_metadata\n\n")
        fid.write("__version__ = importlib_metadata.version(__name__.replace('.', '-'))\n")
        fid.write('"""PyConverter-GeneratedCommands version."""\n')

    print(f"Commands written to {cmd_path}")

    # copy package files to the package directory
    copy_package(_package_path, new_package_path, clean)
    graph_path = get_paths(xml_doc_path)[0]
    shutil.copytree(graph_path, os.path.join(new_package_path, "doc", "source", "images"))

    return cmd_path


def write_docs(commands, cmd_map, package_path):
    """Output to the autogenerated ``package`` directory.

    Parameters
    ----------
    commands : list[XMLCommand]
        List of XML commands.

    cmd_map : dict
        Dictionary with this format: ``{"command_name": "python_name"}``.

    path : str
        Path to the new package folder.

    Returns
    -------
    str
        Path to the new document page.

    """

    doc_package_path = os.path.join(package_path, "doc/source")
    if not os.path.isdir(doc_package_path):
        os.makedirs(doc_package_path)

    doc_src = os.path.join(doc_package_path, "docs.rst")
    with open(doc_src, "w") as fid:
        fid.write("Autosummary\n")
        fid.write("===========\n\n")

        fid.write(".. currentmodule:: pyconverter.generatedcommands\n\n")
        fid.write(".. autosummary::\n")
        fid.write("   :template: base.rst\n")
        fid.write("   :toctree: _autosummary/\n\n")
        for ans_name in commands:
            if ans_name not in SKIP_XML:
                cmd_name = cmd_map[ans_name]
                fid.write(f"   {cmd_name}\n")

    return doc_src

import glob
import os
import shutil

from pydita.ast import ast_tree as ast
from pydita.ast import directory_format as path
from pydita.ast import load_xml_doc as load
from tqdm import tqdm

generated_src_code = os.path.join("src", "pydita", "generatedcommands")

# map APDL command to pymapdl function
CMD_MAP = {}

# common statements used within the docs to avoid duplication
CONST = {
    "Dtl?": "",
    "Caret?": "",
    "Caret1?": "",
    "Caret 40?": "",
    '``"``': "``",
}

# APDL commands to skip
SKIP_APDL = {"*IF", "*ELSE", "C***", "*RETURN", "*DEL"}
SKIP_PYMAPDL = {"if", "else", "c", "return", "del"}


def nested_exec(text):
    """Nested execute."""
    exec(text)


def convert(directory_path, command=None):
    """Covert an XML directory into an RST one."""

    graph_path, link_path, term_path, xml_path = path.get_paths(directory_path)
    links = load.load_links(link_path)
    fcache = load.load_fcache(graph_path)
    docu_global = load.load_docu_global(term_path)
    terms, version_variables = load.load_terms(term_path, docu_global, links, fcache)

    def load_commands(
        xml_path,
        meta_only=False,
    ):
        """Scrape the command info from the MAPDL XML command reference.

        Parameters
        ----------
        xml_path : str
            Path to the directory containing the XML files to be converted.

        Examples
        --------
        >>> from convert import load_commands
        >>> commands = load_commands(
        ...     '/home/user/source/mapdl-cmd-doc/docu_files/ans_cmd/'
        ... )

        """
        if not os.path.isdir(xml_path):
            raise FileNotFoundError(f'Invalid path "{xml_path}"')

        filenames = list(glob.glob(os.path.join(xml_path, "**", "*.xml"), recursive=True))

        if meta_only:
            desc = "Loading command metadata"
        else:
            desc = "Loading commands"

        mapdl_commands = []
        for filename in tqdm(filenames, desc=desc):
            try:
                mapdl_commands.append(
                    ast.MAPDLCommand(
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

        return {cmd.name: cmd for cmd in mapdl_commands}

    command_meta = load_commands(
        os.path.expanduser(xml_path),
        meta_only=True,
    )
    command_names = command_meta.keys()

    # create command mapping between the ansys command name and the pymapdl method.
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
                py_name = lower_name.replace("/", "slash").replace("*", "star")
            else:
                py_name = alpha_name

        CMD_MAP[ans_name] = py_name

    # TODO : accept conversion of a single command

    # convert a single command
    # if command is not None:
    #     if command not in command_meta:
    #         raise ValueError(f"Invalid command {command}")
    #     fname = command_meta[command].xml_filename
    #     cmd = ast.MAPDLCommand(os.path.expanduser(fname), )
    #     commands = {to_py_name(cmd.name): cmd}
    # else:  # convert all commands

    commands = load_commands(xml_path)

    return commands


def copy_package(template_path, new_package_path, clean=False, include_hidden=False):
    """Add files and directory from a template directory path to a new path.

    Parameters
    ----------
    template_path : str
        Path containing the directory to be copied.

    new_package_path : str
        Path containing the directory where the new files and directorys will be added to.

    clean : Bool
        Whether the directorys in new_package_path need to be cleared before adding new files
        or not. The default value is False.

    include_hidden : Bool
        When Python version >= 3.11, the hidden files can be handled automatically when True.
        The default value is False.

    Returns
    -------
    str
        Path containing the source files of the created
        ``ansys-mapdl-commands`` package.

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
        # .vale.ini is considered as a hidden file.
        vale_template = os.path.join(template_path, "doc", ".vale.ini")
        vale_new_path = os.path.join(new_package_path, "doc", ".vale.ini")
        if os.path.isfile(vale_template) and not os.path.isfile(vale_new_path):
            shutil.copy(vale_template, vale_new_path)


def write_source(commands, path, new_package_path=None, clean=True):
    """Write out MAPDL commands as Python source files.

    Parameters
    ----------
    commands : list[MAPDLCommand]
        List of MAPDLCommand.

    path : str
        Path containing ``_package`` directory.

    new_package_path : str
        Path where to copy the ``_package`` directory. Default is ``./package``.

    Returns
    -------
    str
        Path containing the source files of the created
        ``ansys-mapdl-commands`` package.

    """
    template_path = os.path.join(path, "_package")
    if not os.path.isdir(template_path):
        raise FileNotFoundError(
            f"Unable to locate the package templates path at '{template_path}'. "
            f"Expected the _package directory at '{path}'."
        )

    if new_package_path is None:
        new_package_path = os.path.join(path, "package")

    if clean:
        if os.path.isdir(new_package_path):
            shutil.rmtree(new_package_path)

    cmd_path = os.path.join(new_package_path, generated_src_code)
    if not os.path.isdir(cmd_path):
        os.makedirs(cmd_path)

    for ans_name, cmd_obj in tqdm(commands.items(), desc="Writing commands"):
        if ans_name in SKIP_APDL:
            continue
        cmd_name = ast.to_py_name(ans_name)
        path = os.path.join(cmd_path, f"{cmd_name}.py")
        with open(path, "w", encoding="utf-8") as fid:
            fid.write(cmd_obj.to_python())

        try:
            nested_exec(cmd_obj.to_python())
        except:
            raise RuntimeError(f"Failed to execute {cmd_name}.py") from None

    mod_file = os.path.join(cmd_path, "__init__.py")
    with open(mod_file, "w") as fid:
        for ans_name in commands:
            if ans_name in SKIP_APDL:
                continue
            cmd_name = ast.to_py_name(ans_name)
            fid.write(f"from .{cmd_name} import *\n")
        fid.write("try:\n")
        fid.write("    import importlib.metadata as importlib_metadata\n")
        fid.write("except ModuleNotFoundError:\n")
        fid.write("    import importlib_metadata\n\n")
        fid.write("__version__ = importlib_metadata.version(__name__.replace('.', '-'))\n")
        fid.write('"""PyDita-Generatedcommands version."""\n')

    print(f"Commands written to {cmd_path}")

    # copy package files to the package directory
    copy_package(template_path, new_package_path, clean)

    return cmd_path


def write_docs(commands, path):
    """Output to the tinypages directory.

    Parameters
    ----------
    path : str
        Path to the new doc pages directory.

    """

    package_path = os.path.join(path, "package")
    doc_package_path = os.path.join(package_path, "doc/source")
    if not os.path.isdir(doc_package_path):
        os.makedirs(doc_package_path)

    doc_src = os.path.join(doc_package_path, "docs.rst")
    with open(doc_src, "w") as fid:
        fid.write("###########\n")
        fid.write("Autosummary\n")
        fid.write("###########\n")

        fid.write(".. currentmodule:: pydita.generatedcommands\n\n")
        fid.write(".. autosummary::\n")
        fid.write("   :template: base.rst\n")
        fid.write("   :toctree: _autosummary/\n\n")
        for ans_name in commands:
            if ans_name not in SKIP_APDL:
                cmd_name = ast.to_py_name(ans_name)
                fid.write(f"   {cmd_name}\n")

    return doc_src

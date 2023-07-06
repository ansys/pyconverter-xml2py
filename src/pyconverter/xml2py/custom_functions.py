# Copyright (c) 2023 ANSYS, Inc. All rights reserved.

import glob
import os

import numpy as np


def get_docstring_lists(filename):
    """
    Get lists of strings depending on Python file sections.

    Parameters
    ----------
    filename : str
        Path containing the Python file.

    Returns
    -------
    list_py_returns : List[str]
        List containing the docstring ``Returns`` section.
    list_py_examples : List[str]
        List containing the docstring ``Examples`` section.
    list_py_code : List[str]
        List containing the source code.
    list_import : List[str]
        List containing the library import section.
    """
    pyfile = open(filename, "r")
    lines = pyfile.readlines()
    bool_return = False
    bool_notes = False
    bool_examples = False
    begin_docstring = False
    end_docstring = False
    list_py_returns = []
    list_py_examples = []
    list_py_code = []
    list_import = []
    for line in lines:
        if "import" in line:
            list_import.append(line)
        elif "Returns" in line and bool_return is False:
            bool_return = True
            list_py_returns.append(line.strip())
        elif "Notes" in line and bool_notes is False:
            bool_notes = True
        elif "Examples" in line and bool_examples is False:
            bool_examples = True
            list_py_examples.append(line.strip())
        elif '"""' in line and begin_docstring is False:
            begin_docstring = True
        elif '"""' in line and begin_docstring is True:
            end_docstring = True
        elif bool_return is True and np.all(
            np.array([bool_notes, bool_examples, end_docstring]) == False
        ):
            list_py_returns.append(line.strip())
        elif bool_examples is True and end_docstring is False:
            list_py_examples.append(line.strip())
        elif end_docstring is True:
            list_py_code.append(line)
    pyfile.close()
    return list_py_returns, list_py_examples, list_py_code, list_import


# ############################################################################
# CustomFunctions class
# ############################################################################


class CustomFunctions:
    """Provides for creating customized functions."""

    def __init__(self):
        self._path = ""
        self._py_names = []
        self._py_returns = {}
        self._py_examples = {}
        self._py_code = {}
        self._lib_import = {}

    def __init__(self, path):
        self._path = path
        try:
            os.path.isdir(path)
        except:
            raise (FileExistsError, f"The path_functions {path} does not exist.")
        self._py_names = []
        self._py_returns = {}
        self._py_examples = {}
        self._py_code = {}
        self._lib_import = {}
        for filename in list(glob.glob(os.path.join(path, "*.py"))):
            py_name = os.path.split(filename)[-1][:-3]
            self._py_names.append(py_name)
            list_py_returns, list_py_examples, list_py_code, list_import = get_docstring_lists(
                filename
            )
            if len(list_py_returns) > 0:
                self._py_returns[py_name] = list_py_returns
            if len(list_py_examples) > 0:
                self._py_examples[py_name] = list_py_examples
            if len(list_py_code) > 0:
                self._py_code[py_name] = list_py_code
            if len(list_import) > 0:
                self._lib_import[py_name] = list_import

    @property
    def path(self):
        """Path where the customized function files are located."""
        return self._path

    @path.setter
    def path(self, path):
        self._path = path
        try:
            os.path.isdir(path)
        except:
            raise (FileExistsError, f"The path_functions {path} does not exist.")
        self._py_names = []
        for filename in list(glob.glob(os.path.join(path, "*.py"))):
            py_name = os.path.split(filename)[-1][:-3]
            self._py_names.append(py_name)
            list_py_returns, list_py_examples, list_py_code, list_import = get_docstring_lists(
                filename
            )
            if len(list_py_returns) > 0:
                self._py_returns[py_name] = list_py_returns
            if len(list_py_examples) > 0:
                self._py_examples[py_name] = list_py_examples
            if len(list_py_code) > 0:
                self._py_code[py_name] = list_py_code
            if len(list_import) > 0:
                self._lib_import[py_name] = list_import

    @property
    def py_names(self):
        """List with all customized functions located in the folder."""
        return self._py_names

    @property
    def py_returns(self):
        """Dictionary containing the ``Returns`` section if any."""
        return self._py_returns

    @property
    def py_examples(self):
        """Dictionary containing the ``Examples`` section if any."""
        return self._py_examples

    @property
    def py_code(self):
        """Dictionary containing the customized source code."""
        return self._py_code

    @property
    def lib_import(self):
        """Dictionary containing the needed libraries if any."""
        return self._lib_import

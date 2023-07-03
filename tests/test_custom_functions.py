# Copyright (c) 2023 ANSYS, Inc. All rights reserved.

import os
import pydoc.xml2python.custom_functions as cf


def test_customfunctions(custom_functions):
    assert "k" in custom_functions._py_names
    assert "    msg = self.run(command, **kwargs)\n" in custom_functions._py_code["k"]
    assert "import re\n" in custom_functions._lib_import["k"]
    assert "list" in custom_functions._py_returns["kdist"]
    assert "Compute the distance between two keypoints." in custom_functions._py_examples["kdist"]


def test_get_docstring_lists(path_custom_functions):
    path_custom_function = os.path.join(path_custom_functions, "kdist.py")
    list_py_returns, list_py_examples, list_py_code, list_import = cf.get_docstring_lists(
        path_custom_function
    )
    "list" in list_py_returns
    "Compute the distance between two keypoints." in list_py_examples
    'return parse.parse_kdist(self.run(f"KDIST,{kp1},{kp2}", **kwargs))' in list_py_code
    "import parse\n" in list_import

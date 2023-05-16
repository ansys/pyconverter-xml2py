import glob
import os
import numpy as np

def get_docstring_list(filename):
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
    for line in lines:
        print(line)
        if "Returns" in line and bool_return is False:
            print("There is a return")
            bool_return = True
            list_py_returns.append(line[4:-1])
        elif "Notes" in line and bool_notes is False:
            bool_notes = True
        elif "Examples" in line and bool_examples is False:
            bool_examples = True
            list_py_examples.append(line[4:-1])
        elif '"""' in line and ([begin_docstring, begin_docstring] == [False, False]):
            begin_docstring = True
        elif '"""' in line and begin_docstring is True:
            end_docstring = True
        
        elif bool_return is True and np.all(np.array([bool_notes, bool_examples, end_docstring])==False):
            list_py_returns.append(line[4:-1])
        
        elif bool_examples is True and end_docstring is False:
            list_py_examples.append(line[4:-1])
        
        elif end_docstring is True:
            list_py_code.append(line[4:])
    
    return list_py_returns, list_py_examples, list_py_code

# ############################################################################
# CustomFunctions class
# ############################################################################

class CustomFunctions:
    """Functions that need to be customized."""

    def __init__(self):
        self._path = ""
        self._py_names = []
        self._py_returns = {}
        self._py_examples = {}
        self._py_code = {}

    def __init__(self, path):
        print(path)
        self._path = path
        try:
            os.path.isdir(path)
        except:
            raise (FileExistsError, f"The path_functions {path} does not exist.")
        self._py_names = []
        self._py_returns = {}
        self._py_examples = {}
        self._py_code = {}
        for filename in list(glob.glob(os.path.join(path, "*.py"))):
            py_name = os.path.split(filename)[-1][:-3]
            self._py_names.append(py_name)
            list_py_returns, list_py_examples, list_py_code = get_docstring_list(filename)
            if len(list_py_returns)>0:
                self._py_returns[py_name] = list_py_returns
            if len(list_py_examples)>0:
                self._py_examples[py_name] = list_py_examples
            if len(list_py_code)>0:
                self._py_code[py_name] = list_py_code

    @property
    def path(self):
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
            list_py_returns, list_py_examples, list_py_code = get_docstring_list(filename)
            if len(list_py_returns)>0:
                self._py_returns[py_name] = list_py_returns
            if len(list_py_examples)>0:
                self._py_examples[py_name] = list_py_examples
            if len(list_py_code)>0:
                self._py_code[py_name] = list_py_code


    @property
    def py_names(self):
        return self._py_names

    @property
    def py_returns(self):
        return self._py_returns

    @property
    def py_examples(self):
        return self._py_examples

    @property
    def py_code(self):
        return self._py_code

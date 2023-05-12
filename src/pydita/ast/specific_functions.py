import glob
import os

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

    def __init__(self, path):
        print(path)
        self._path = path
        try:
            os.path.isdir(path)
        except:
            raise (FileExistsError, f"The path_functions {path} does not exist.")
        self._py_names = []
        for filename in list(glob.glob(os.path.join(path, "*.py"))):
            self._py_names.append(os.path.split(filename)[-1][:-3])
        self._py_returns = {}
        self._py_examples = {}

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
            self._py_names.append(os.path.split(filename)[-1][:-3])

    @property
    def py_names(self):
        return self._py_names

    @property
    def py_returns(self):
        pass

    @property
    def py_examples(self):
        pass

    @property
    def py_code(self):
        pass

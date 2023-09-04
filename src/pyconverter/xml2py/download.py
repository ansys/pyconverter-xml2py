"""Functions to download template datasets from the pyconverter-xml2py repository.
"""

import os
import shutil


def fix_gitdir():
    """Remove empty folders added by gitdit while downloading the template folder."""

    for (path, fold, _) in os.walk("_package", topdown=True):
        if "_package" in fold:
            print("removing : ", os.path.join(path, "_package"))
            shutil.rmtree(os.path.join(path, "_package"))  # this is due because


def download_template():
    """Download the templage package provided by default."""

    os.system("gitdir https://github.com/ansys/pyconverter-xml2py/tree/main/_package")
    fix_gitdir()
    print("The default template package has been downloaded.")

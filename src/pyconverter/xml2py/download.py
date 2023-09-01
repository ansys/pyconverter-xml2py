"""Functions to download template datasets from the pyconverter-xml2py repository.
"""

import os
import shutil

def download_template():
    """Download the templage package provided by default."""
    # init_cwd = os.getcwd()
    # change = False
    # if output_dir!="":
    #     if not os.path.isdir(output_dir):
    #         raise ValueError(f"The directory provided {output_dir} doesn't exist.")
    #     elif output_dir != os.getcwd():
    #         os.chdir(output_dir)
    #         change = True
    os.system("gitdir https://github.com/ansys/pyconverter-xml2py/tree/main/_package")
    
    for (path,fold,_) in os.walk('_package', topdown=True):
        if "_package" in fold:
            print("removing : ", os.path.join(path, "_package"))
            shutil.rmtree(os.path.join(path, "_package")) # this is due because gitdir add useless folders while copy pasting
    
    # if change is True:
    #     os.chdir(init_cwd)
    
download_template("temp")
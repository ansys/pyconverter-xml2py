Getting Started
===============

Pre-defined format
------------------

The pre-defined XML directory format is as follow:

.. include:: ./diags/diag_directory.rst

Converting an `XML-directory`
-----------------------------

Once the `XML_directory` is correctly organized, the converter can be used.

.. code:: bash

    python xml2rst.py -p XML_directory_path

Once the directory is converted, the Sphinx documentation can be generated.
The generated documentation is by default contained in the `package` directory.

The following code is to render the documentation as an HTML one from Windows:

.. code:: bash

    cd package
    pip install -e .[doc,tests] # Using a virtual environment is recommended.
    .\doc\make.bat html 

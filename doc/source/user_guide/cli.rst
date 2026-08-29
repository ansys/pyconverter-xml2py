Command Line Interface
======================

PyConverter-XML2Py provides a command-line interface (CLI) for converting XML documentation
into Python packages with Sphinx documentation.

After installing PyConverter-XML2Py, the CLI is available as the ``pyconverter-xml2py`` command.
Documentation to install the package can be found in the :ref:`installation` section.


Quick Start
-----------

The most basic usage requires only the path to your XML documentation:

.. code:: bash

    pyconverter-xml2py package -x /path/to/xml/docs

This will create a Python package in the current directory with the default template and settings.

Available Commands
------------------

.. click:: pyconverter.xml2py.cli:main
   :prog: pyconverter-xml2py
   :nested: full


Environment Variables
---------------------

.. envvar:: XML_PATH

    Default path for XML documentation directory. If set, you don't need to
    provide the ``-x`` option.

    .. code:: bash

        export XML_PATH=/path/to/xml/docs
        pyconverter-xml2py package -p /path/to/output

Usage Examples
--------------

**Minimal example:**

Convert XML docs to Python package in current directory:

.. code:: bash

    pyconverter-xml2py package \
        --xml-path ./xml_documentation \


**Complete example:**

Convert with all options:

.. code:: bash

    pyconverter-xml2py package \
        --xml-path ./xml_documentation \
        --targ-path ./my_package_output \
        --template-path ./my_template \
        --func-path ./my_custom_functions \
        --run-pre-commit \
        --max-length 150

**Using environment variables:**

.. code:: bash

    export XML_PATH=./xml_documentation
    pyconverter-xml2py package --targ-path ./output --run-pre-commit

**Check version:**

.. code:: bash

    pyconverter-xml2py version

Troubleshooting
---------------

**Common Issues:**

1. **"Missing the XML documentation path"**: Make sure to provide either ``-x`` option or set the ``XML_PATH`` environment variable.

2. **"Please, enter a valid directory path"**: Ensure the XML path exists and contains the proper directory structure.

3. **File encoding errors**: On Windows, make sure your XML files are properly encoded (UTF-8 is recommended).

**Getting Help:**

Use the ``--help`` flag to get detailed help for any command:

.. code:: bash

    pyconverter-xml2py --help
    pyconverter-xml2py package --help


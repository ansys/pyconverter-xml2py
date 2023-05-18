PyDita-AST
==========

A Python wrapper to convert XML documentation into RST files and the Sphinx documentation.

|pyansys| |pypi| |GH-CI| |codecov| |MIT| |black|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |pypi| image:: https://img.shields.io/pypi/v/pydita-ast.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/pydita_ast/

.. |codecov| image:: https://codecov.io/gh/ansys/pydita-ast/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/ansys/pydita-ast

.. |GH-CI| image:: https://github.com/ansys/pydita-ast/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/pydita-ast/actions/workflows/ci_cd.yml

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
  :target: https://github.com/psf/black
  :alt: black


Overview
--------

The PyDita-AST project aims to automatically generate a Python library and a related 
Sphinx documentation from an XML documentation.


Documentation and issues
------------------------

On the `PyDita-AST Issues <https://github.com/ansys/pydita-ast/issues>`_ for this repository,
you can create issues to submit questions, report bugs, and request new features. 
To reach the PyAnsys support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.


Getting started
---------------

Install the ``pydita-ast`` package with:

.. code:: bash

   python -m pip install pydita-ast


It is recommended to organize the XML documentation as follow:

.. image:: ./doc/source/getting_started/images/diags/graphviz-diag_directory.png
   :width: 450
   :align: center


Converting an XML-directory
---------------------------

Once the ``XML_directory`` is correctly organized, the converter can be run.

.. code:: bash

    python xml2rst.py -p XML_directory_path

After that, the Sphinx documentation can be generated. By default, it is
contained in the ``package`` directory.

The following code is to render the documentation as an HTML one from Windows:

.. code:: bash

    cd package
    pip install -e .[doc,tests] # Using a virtual environment is recommended.
    .\doc\make.bat html 

User guide
==========

How to install
--------------

At least two installation modes are provided: user and developer.

For users
^^^^^^^^^

User installation can be performed by running:

.. code:: bash

    python -m pip install pydita-ast

For developers
^^^^^^^^^^^^^^

Installing PyDita-AST in developer mode allows
you to modify the source and enhance it.

Before contributing to the project, please refer to the `PyAnsys Developer's guide`_. You will 
need to follow these steps:

#. Start by cloning this repository:

    .. code:: bash

        git clone https://github.com/ansys/pydita-ast

#. Create a fresh-clean Python environment and activate it. Refer to the
   official `venv`_ documentation if you require further information:

    .. code:: bash

        # Create a virtual environment
        python -m venv .venv

        # Activate it in a POSIX system
        source .venv/bin/activate

        # Activate it in Windows CMD environment
        .venv\Scripts\activate.bat

        # Activate it in Windows Powershell
        .venv\Scripts\Activate.ps1

#. Make sure you have the latest version of `pip`_:

    .. code:: bash

        python -m pip install -U pip

#. Install the project in editable mode:

    .. code:: bash
    
        python -m pip install -e .

#. Install additional requirements (if needed):

     .. code:: bash

        python -m pip install .[doc,tests]

#. Finally, verify your development installation by running:

    .. code:: bash
        
        pytest tests -v


Style and testing
-----------------

If required, you can always call the style commands (`black`_, `isort`_,
`flake8`_, etc) or unit testing ones (`pytest`_) from the command line. However,
this does not guarantee that your project is being tested in an isolated
environment, which is another reason to consider using `tox`_.


Documentation
-------------

For building documentation, you can either run the usual rules provided in the
`Sphinx`_ Makefile, such as:

.. code:: bash

    python -m pip install .[doc]
    make -C doc/ html

    # subsequently open the documentation with (under Linux):
    your_browser_name doc/html/index.html

Distributing
------------

If you would like to create either source or wheel files, start by installing
the building requirements:

.. code:: bash

    python -m pip install -e .[doc,tests]

Then, you can execute:

    .. code:: bash

        python -m build
        python -m twine check dist/*


.. LINKS AND REFERENCES
.. _black: https://github.com/psf/black
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _isort: https://github.com/PyCQA/isort
.. _PyAnsys Developer's guide: https://dev.docs.pyansys.com/
.. _pre-commit: https://pre-commit.com/
.. _pytest: https://docs.pytest.org/en/stable/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _pip: https://pypi.org/project/pip/
.. _tox: https://tox.wiki/
.. _venv: https://docs.python.org/3/library/venv.html
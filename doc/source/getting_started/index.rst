Getting started
===============

Installation
------------

Two installation modes of the ``pyconverter-xml2py`` package are provided: user and developer.

User installation
^^^^^^^^^^^^^^^^^

Install the latest release for use with this command:

.. code:: bash

    python -m pip install pyconverter-xml2py


For developers
^^^^^^^^^^^^^^

Installing the ``pyconverter-xml2py`` package in developer mode allows
you to modify the source and enhance it.

Before contributing to the project, see the `PyAnsys Developer's Guide`_.

Follow these steps to install the package in developer mode:

#. Clone the repository:

    .. code:: bash

        git clone https://github.com/ansys/pyconverter-xml2py

#. Create a fresh-clean Python environment and activate it. If you require
   additional information on creation of a virtual environment, see the
   official Python `venv`_ documentation.

    .. tab-set::

      .. tab-item:: Linux
        :sync: linux

        ::

          python -m venv venv
          source venv/bin/activate

      .. tab-item:: macOS
        :sync: macos

        ::

          python -m venv venv
          source venv/bin/activate

      .. tab-item:: Windows
        :sync: windows

        ::

          python -m venv venv
          .\venv\Scripts\activate


#. Make sure you have the latest version of `pip`_:

    .. code:: bash

        python -m pip install -U pip

#. Install the project in editable mode:

    .. code:: bash

        python -m pip install -e .

#. Install additional requirements (if needed):

     .. code:: bash

        python -m pip install .[doc,tests]

#. Verify your development installation:

    .. code:: bash

        pytest tests -v


Style and testing
-----------------

If required, you can call style commands (such as `black`_, `isort`_,
and `flake8`_) or unit testing commands (such as `pytest`_) from the command line.
However, this does not guarantee that your project is being tested in an isolated
environment, which is why you might consider using `tox`_.


Documentation
-------------

For building documentation, you can run the usual rules provided in the
`Sphinx`_ Makefile or make.bat:

.. tab-set::

  .. tab-item:: Makefile

    ::

      python -m pip install .[doc]
      make -C doc/ html


  .. tab-item:: make.bat

    ::

      python -m pip install .[doc]
      .\doc\make.bat html

Once the documentation is built, you can open it as follow.

.. tab-set::

  .. tab-item:: Linux
      :sync: linux

      By running the command: 
      ::

        your_browser_name doc/html/index.html

  .. tab-item:: macOS
      :sync: macos

      By opening the documentation from your file explorer located in ``doc/html/index.html``.

  .. tab-item:: Windows
      :sync: windows

      By opening the documentation from your file explorer located in ``doc/html/index.html``.



Distributing
------------

If you would like to create either source or wheel files, start by installing
the building requirements:

.. code:: bash

    python -m pip install -e .[doc,tests]

Then, execute these commands:

    .. code:: bash

        python -m build
        python -m twine check dist/*

.. _ref_contributing:

Contribute
==========

Overall guidance on contributing to a PyAnsys library appears in the
`Contributing <dev_guide_contributing_>`_ topic
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar
with this guide before attempting to contribute to PyDita-AST.

The following contribution information is specific to PyDita-AST.

Clone the repository
--------------------

Run this code to clone and install the latest version of PyDita-AST in development mode::

    git clone https://github.com/pyansys/pydita-ast
    cd pydita-ast
    python -m pip install --upgrade pip
    pip install -e .

Post issues
-----------

Use the `PyDita-AST Issues <pydita_ast_issues_>`_ page to submit questions,
report bugs, and request new features. When possible, use these issue
templates:

* Bug report template
* Feature request template

If your issue does not fit into one of these categories, create your own issue.

To reach the PyAnsys support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.


Build documentation
-------------------

To build the PyDita-AST documentation locally, in the root directory of the repository, run::
    
    pip install .[doc]
    .\doc\make.bat html 

Documentation for the latest stable release of PyDita-AST is hosted at
`PyDita-AST Documentation <pydita_ast_docs_>`_.

Documentation for the latest development version, which tracks the
``main`` branch, is hosted at 
`Development PyDita-AST Documentation <pydita_ast_dev_docs_>`_.
This version is automatically kept up to date via GitHub actions.


Adhere to code style
--------------------

PyDita-AST follows the PEP8 standard as outlined in the `PyAnsys Development Guide
<dev_guide_pyansys_>`_ and implements style checking using
`pre-commit <precommit_>`_.

To ensure your code meets minimum code styling standards, run this code::

  pip install pre-commit
  pre-commit run --all-files

You can also install this as a pre-commit hook by running this code::

  pre-commit install

This way, it's not possible for you to push code that fails the style checks::

  $ pre-commit install
  $ git commit -am "added my cool feature"
  black....................................................................Passed
  blacken-docs.............................................................Passed
  isort....................................................................Passed
  flake8...................................................................Passed
  codespell................................................................Passed
  check for merge conflicts................................................Passed
  debug statements (python)................................................Passed
  Validate GitHub Workflows................................................Passed
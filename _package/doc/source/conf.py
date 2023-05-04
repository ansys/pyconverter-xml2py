from datetime import datetime
import os
import sys

# -- General configuration ------------------------------------------------

extensions = ["pyvista.ext.plot_directive"]
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"

project = "Documentation"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS Inc."

release = version = "0.1.dev"
exclude_patterns = ["_build"]
pygments_style = "sphinx"

extensions = [
    "notfound.extension",
    "numpydoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx.ext.mathjax",
    "linuxdoc.rstFlatTable",
]

# # Intersphinx mapping
# intersphinx_mapping = {
#     "python": ("https://docs.python.org/dev", None),
#     "scipy": ("https://docs.scipy.org/doc/scipy/", None),
#     "numpy": ("https://numpy.org/devdocs", None),
#     "matplotlib": ("https://matplotlib.org/stable", None),
#     "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
#     "pyvista": ("https://docs.pyvista.org/", None),
#     "grpc": ("https://grpc.github.io/grpc/python/", None),
# }

# The suffix(es) of source filenames.
source_suffix = ".rst"
language = "en"

# Copy button customization ---------------------------------------------------
# exclude traditional Python prompts from the copied code
copybutton_prompt_text = r">>> ?|\.\.\. "
copybutton_prompt_is_regexp = True

# numpydoc configuration ------------------------------------------------------
numpydoc_use_plots = True
numpydoc_show_class_members = False
numpydoc_xref_param_type = True
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    # "SS03", # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}


# -- Options for HTML output -------------------------------------------------
html_short_title = html_title = "Documentation"
html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "show_prev_next": False,
}

html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": "pyansys",
    "github_repo": "pydita-ast",
    "github_version": "main",
}
# -- Options for HTMLHelp output ---------------------------------------------

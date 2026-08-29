Configuration Files
===================

PyConverter-XML2Py uses configuration files to customize the conversion process.
The main configuration is stored in ``config.yaml``.

config.yaml Structure
---------------------

The ``config.yaml`` file controls various aspects of the package generation process:

.. code:: yaml

    # Package metadata
    new_package_name: "package"
    project_name: "MyProject"
    
    # Directory structure
    library_name_structured: ["src", "myproject"]
    subfolders: ["subfolder1", "subfolder2"]
    image_folder_path: "images"

    # Command processing
    rules:
      "/": slash
      "*": star

    ignored_commands:
        - "COMMAND1"
        - "COMMAND2"
    
    specific_command_mapping:
        "OLD_NAME": "new_name"
    
    specific_classes:
        "OldClassName": "NewClassName"
    
    # Custom comments for commands
    comments:
        - msg: "Custom comment text"
          type: "warning"
          command: ["COMMAND3", "COMMAND4"]
        - msg: "Another comment"
          type: "note"
          command: ["COMMAND5"]
       

Configuration Options
---------------------

Package Metadata
^^^^^^^^^^^^^^^^^

.. option:: new_package_name

    The name of the generated package directory.
    
    **Default:** ``"package"``

.. option:: project_name

    The display name of the project used in documentation.

Directory Structure
^^^^^^^^^^^^^^^^^^^

.. option:: library_name

    List defining the nested directory structure for the generated Python modules.
    
    **Example:** ``["src", "myproject"]`` creates ``src/myproject/`` structure

.. option:: subfolders

    List of subfolders where to place the converted files within the package.
    
    **Example:** ``["subfolder1", "subfolder2"]`` creates additional directories under the package.

.. option:: image_folder_path

    Relative path where images from the XML documentation will be added.
    
    **Default:** ``"images"``

Command Processing
^^^^^^^^^^^^^^^^^^

.. option:: rules

    Dictionary defining how to handle specific commands or patterns during conversion.
    
    **Example:** ``{"/": "slash", "*": "star"}`` maps commands starting with `/` to `slash` and `*` to `star`.

.. option:: ignored_commands

    List of command names to skip during conversion.
    
    **Type:** List of strings

.. option:: specific_command_mapping

    Dictionary mapping original command names to custom Python function names.
    
    **Example:** ``{"/CLEAR": "clear_all", "*GET": "get_parameter"}``

.. option:: specific_classes

    Dictionary mapping original class names to custom class names.
    
    **Example:** ``{"Mesh Controls": "Meshing Controls", "Solver Settings": "Solution Settings"}``

Custom comments
^^^^^^^^^^^^^^^

.. option:: comments

    Custom comments for specific commands.

    **Type:** List of dictionaries with keys `msg`, `type`, and `command`.


Template Configuration
----------------------

When using custom templates, you can override the default template structure
by providing a ``template_path`` to the CLI or by placing a custom template
in the ``_package`` directory.

The template directory should contain:

.. code:: text

    _package/
    ├── pyproject.toml
    ├── README.rst
    ├── LICENSE
    ├── AUTHORS.md
    ├── pre-commit-config.yaml
    └── doc/
        ├── Makefile
        ├── make.bat
        ├── .vale.ini
        ├── source/
        │   ├── conf.py
        │   ├── index.rst
        │   └── _templates/          # if needed
        └── styles/
            └── .gitignore
            └── Vocab/

Custom Function Configuration
-----------------------------

For information about configuring custom functions, see :doc:`customized_functions`.

Example Configuration
---------------------

Here's a complete example ``config.yaml``:

.. code:: yaml

    new_package_name: "my_generated_package"
    project_name: "My ANSYS Package"
    
    library_name_structured: ["src", "ansys", "mypackage"]
    subfolders: ["utilities", "data_processing"]
    image_folder_path: "../images"
    
    rules:
      "/": "slash"
      "*": "star"

    ignored_commands:
        - "OBSOLETE_CMD"
        - "DEPRECATED_FUNC"
    
    specific_command_mapping:
        "/CLEAR": "clear_all"
        "*GET": "get_parameter"
    
    specific_classes:
        "MeshControls": "MeshingControls"
        "SolverSettings": "SolutionSettings"
    
    comments:
        - msg: "This command is deprecated, use 'new_command' instead."
          type: "warning"
          command: ["OLD_COMMAND"]

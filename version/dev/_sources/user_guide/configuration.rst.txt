.. _ref_configuration:

Configuration reference
=======================

The ``config.yaml`` file is the central configuration file for PyConverter-XML2Py.
It controls various aspects of code generation, including project structure,
command mapping, and class inheritance.

This section provides a comprehensive reference for all available configuration options.


File location
-------------

The ``config.yaml`` file should be located in the root directory of your project,
alongside the converter executable.


Configuration options
---------------------


Project metadata
~~~~~~~~~~~~~~~~

``project_name``
^^^^^^^^^^^^^^^^

**Type:** String

**Description:** Name of the generated project.

**Example:**

.. code-block:: yaml

    project_name: PyConverter-GeneratedCommands


``library_name_structured``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Type:** List of strings

**Description:** Defines the nested package structure for the generated library.
The converter creates a directory hierarchy based on this list.

**Example:**

.. code-block:: yaml

    library_name_structured:
      - pyconverter
      - generatedcommands

This generates the structure: ``src/pyconverter/generatedcommands/``


``subfolders``
^^^^^^^^^^^^^^

**Type:** List of strings

**Description:** Additional subfolders to create within the library structure.
Useful for organizing generated code into deeper hierarchies.

**Example:**

.. code-block:: yaml

    subfolders:
      - subfolder
      - subsubfolder

This adds: ``src/pyconverter/generatedcommands/subfolder/subsubfolder/``


``new_package_name``
^^^^^^^^^^^^^^^^^^^^

**Type:** String

**Description:** Name of the directory where the generated package is created.

**Default:** ``package``

**Example:**

.. code-block:: yaml

    new_package_name: package


``image_folder_path``
^^^^^^^^^^^^^^^^^^^^^

**Type:** String

**Description:** Relative path where command images are stored in the generated
documentation.

**Example:**

.. code-block:: yaml

    image_folder_path: ../images/_commands


Command name mapping
~~~~~~~~~~~~~~~~~~~~

``rules``
^^^^^^^^^

**Type:** Dictionary (key-value pairs)

**Description:** Defines character replacement rules for converting command names
to valid Python identifiers. Useful for handling special characters in command names.

**Example:**

.. code-block:: yaml

    rules:
      "/": slash
      "*": star

- Command ``/PREP7`` becomes ``prep7()``
- Command ``*GET`` becomes ``starget()`` or ``get()`` (depending on additional rules)


``specific_command_mapping``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Type:** Dictionary (key-value pairs)

**Description:** Explicitly maps specific command names to Python function names.
Takes precedence over general rules.

**Example:**

.. code-block:: yaml

    specific_command_mapping:
      "*DEL": stardel
      "C***": c
      "/INQUIRE": inquire


Command filtering
~~~~~~~~~~~~~~~~~

``ignored_commands``
^^^^^^^^^^^^^^^^^^^^

**Type:** List of strings

**Description:** Commands to exclude from code generation. Useful for commands
that are already implemented elsewhere or should not be converted.

**Example:**

.. code-block:: yaml

    ignored_commands:
      - "*ASK"
      - "*VEDIT"
      - "/ERASE"
      - "HELP"
      - "/EXIT"

Commands in this list are skipped during conversion and do not generate Python methods.


Documentation annotations
~~~~~~~~~~~~~~~~~~~~~~~~~

``comments``
^^^^^^^^^^^^

**Type:** List of comment objects

**Description:** Adds custom messages to specific command documentation. Each comment
object has three fields:

- ``msg``: The message text (supports reStructuredText formatting)
- ``type``: Message type (``"warning"``, ``"note"``, ``"tip"``, etc.)
- ``commands``: List of commands to annotate

**Example:**

.. code-block:: yaml

    comments:
      - msg: 'This command must be run using :func:`non_interactive`.'
        type: "warning"
        commands:
          - "*CREATE"
          - "CFOPEN"
          - "*VWRITE"
      
      - msg: 'Starting with v0.66.0, you can use "P" for interactive selection.'
        type: "note"
        commands:
          - "ASEL"

The message appears as a Sphinx admonition in the generated documentation:

.. warning::
   This command must be run using :func:`non_interactive`.


Class organization
~~~~~~~~~~~~~~~~~~

``specific_classes``
^^^^^^^^^^^^^^^^^^^^

**Type:** Dictionary (key-value pairs)

**Description:** Renames classes generated from command groups. By default, classes
are named based on the command group name, but this option allows customization.

**Example:**

.. code-block:: yaml

    specific_classes:
      2D to 3D Analysis: Analysis 2D to 3D
      Parameters: Parameter definition

- The class for "2D to 3D Analysis" commands is named ``Analysis2Dto3D``
- The class for "Parameters" commands is named ``ParameterDefinition``


Base class inheritance
~~~~~~~~~~~~~~~~~~~~~~

``base_class``
^^^^^^^^^^^^^^

**Type:** Object with ``rules`` list

**Description:** Configures pattern-based inheritance for generated classes. This
allows generated classes to inherit from a base class.

**Structure:**

.. code-block:: yaml

    base_class:
      rules:
        - pattern: "pattern_string"
          module: "module.path"
          class_name: "BaseClassName"

**Fields:**

- ``pattern``: Glob pattern to match against ``"module_name/class_name"``
- ``module``: Python module path to import the base class from
- ``class_name``: Name of the base class to inherit from

**Pattern matching:**

Patterns are matched against the full path ``"module_name/class_name"`` and support
wildcards:

- ``"*"`` - Matches all classes
- ``"module_name/*"`` - Matches all classes in a specific module
- ``"module_name/ClassName"`` - Matches a specific class
- ``"*/ClassName"`` - Matches any class named ``ClassName`` in any module

**Rule evaluation:** Rules are evaluated in order, and the **first matching rule wins**.
This allows you to define specific overrides followed by general fallback patterns.

**Example 1: All classes inherit from the same base**

.. code-block:: yaml

    base_class:
      rules:
        - pattern: "*"
          module: "ansys.mapdl.core"
          class_name: "BaseCommandClass"

Generates:

.. code-block:: python

    from ansys.mapdl.core import BaseCommandClass


    class Abbreviations(BaseCommandClass):
        def method(self):
            pass

**Example 2: Module-specific inheritance**

.. code-block:: yaml

    base_class:
      rules:
        - pattern: "apdl/*"
          module: "ansys.mapdl.core.apdl"
          class_name: "APDLBase"
        
        - pattern: "prep7/*"
          module: "ansys.mapdl.core.prep"
          class_name: "PrepBase"

**Example 3: Specific class with fallback**

.. code-block:: yaml

    base_class:
      rules:
        - pattern: "prep7/Meshing"
          module: "ansys.mapdl.core.prep.special"
          class_name: "SpecialMeshingBase"
        
        - pattern: "prep7/*"
          module: "ansys.mapdl.core.prep"
          class_name: "PrepBase"
        
        - pattern: "*"
          module: "ansys.mapdl.core"
          class_name: "BaseCommandClass"

In this example:

- ``prep7/Meshing`` gets ``SpecialMeshingBase``
- Other ``prep7`` classes get ``PrepBase``
- All other classes get ``BaseCommandClass``

**Default behavior:** If no ``base_class`` configuration is provided or no pattern
matches, classes are generated without inheritance:

.. code-block:: python

    class Abbreviations:
        def method(self):
            pass


Complete example
----------------

Here is a complete ``config.yaml`` file showing all options:

.. code-block:: yaml

    # Project metadata
    project_name: PyConverter-GeneratedCommands
    
    library_name_structured:
      - pyconverter
      - generatedcommands
    
    subfolders:
      - subfolder
      - subsubfolder
    
    new_package_name: package
    
    image_folder_path: ../images/_commands
    
    # Command name mapping
    rules:
      "/": slash
      "*": star
    
    specific_command_mapping:
      "*DEL": stardel
      "C***": c
      "/INQUIRE": inquire
    
    # Command filtering
    ignored_commands:
      - "*ASK"
      - "*VEDIT"
      - "/ERASE"
      - "HELP"
      - "/EXIT"
    
    # Documentation annotations
    comments:
      - msg: 'This command requires special handling.'
        type: "warning"
        commands:
          - "*CREATE"
          - "*VWRITE"
    
    # Class organization
    specific_classes:
      2D to 3D Analysis: Analysis 2D to 3D
      Parameters: Parameter definition
    
    # Base class inheritance
    base_class:
      rules:
        - pattern: "prep7/Meshing"
          module: "ansys.mapdl.core.prep"
          class_name: "PrepBase"
        
        - pattern: "apdl/*"
          module: "ansys.mapdl.core.apdl"
          class_name: "APDLBase"
        
        - pattern: "*"
          module: "ansys.mapdl.core"
          class_name: "BaseCommandClass"



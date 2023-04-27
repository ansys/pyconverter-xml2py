Getting Started
===============

Pre-defined format
------------------

The pre-defined XML folder format is as follow:

.. code:: bash

    XML_folder/
    │
    ├── graphics/
    │   ├── .gifs files
    │   └── images files
    |
    ├── links/
    │   └── .db files
    |
    ├── terms/
    │   ├── glb/
    │   │   ├── variable_file       #default value is build_variables.ent
    │   │   ├── global_terms_file   #default value is terms_global.ent
    │   │   └── manual_file         #default value is manuals.ent
    │   └── character_folder/       #default value is ent/
    │       └── .ent files
    └── xml/
        ├── subfolders/
        │   ├── .xml files
        │   └── mathgraphics_folder/
        │       └── .svg files
        ├── .xml files
        └── .ent files


Converting an `XML-folder`
--------------------------

Once the `XML_folder` is correctly organized, the converter can be used.

.. code:: bash

    python xml2rst.py -p XML_folder_path

Once the folder is converted, the Sphinx documentation can be generated.
The generated documentation is by default contained in the `package` folder.

The following code is to render the documentation as an HTML one from Windows:

.. code:: bash

    cd package
    pip install -e .[doc,tests] # Using a virtual environment is recommended.
    .\doc\make.bat html 

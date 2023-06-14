# Copyright (c) 2023 ANSYS, Inc. All rights reserved.

import argparse
import os

# Predefined directory format

# XML_directory/
# │
# ├── graphics/
# │   ├── .gifs files
# │   └── images files
# |
# ├── links/
# │   └── .db files
# |
# ├── terms/
# │   ├── glb/
# │   │   ├── variable_file         #default value is build_variables.ent
# │   │   ├── global_terms_file     #default value is terms_global.ent
# │   │   └── manual_file           #default value is manuals.ent
# │   └── character_directory/         #default value is ent/
# │       └── .ent files
# └── xml/
#     ├── subdirectorys/
#     │   ├── .xml files
#     │   └── mathgraphics_directory/   #this is a defalut value
#     │       └── .svg files
#     ├── .xml files
#     └── .ent files


def xml_path(path=None):
    """Return the path to the directory containing the XML documentation.
    You should follow the predefined directory structure.

    Parameters
    ----------
    path : str, optional
        Path of the XML documentation to convert. The default is ``None``,
        in which case the path is set with either the argument parser ``-p`` or
        ``--xml-path``, or with the ``XML_PATH`` environment variable.

    Returns
    -------
    path : str
        Path of the XML documentation to convert.

    """
    if path is None:
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument("--xml-path", "-p", help="XML Documentation path")
            args = parser.parse_args()
            path = args.xml_path
        except:
            try:
                path = os.environ.get("XML_PATH")
            except:
                pass

    if path is None:
        raise RuntimeError(
            "Missing the XML documentation path. Specify this with either --xml-path, -p, or set the XML_PATH environment variable"  # noqa : E501
        )

    path = os.path.abspath(os.path.expanduser(path))

    # Verification
    if not os.path.isdir(path):
        raise FileNotFoundError(f"Documentation path at {path} does not exist")

    return path


def get_paths(path, graph_path=None, link_path=None, term_path=None, xml_path=None):
    """Get the paths to the directories needed for the conversion.

    Parameters
    ----------
    path : str
        Path to the directory with the predefined format.

    graph_path : str, optional
        Path to the directory containing the graphics. The default is ``None``,
        in which case the XML predefined directory format is used.

    link_path : str, optional
        Path to the directory containing the links. The default is ``None``,
        in which case the XML predefined directory format is used.

    term_path : str, optional
        Path to the directory containing the terms. The default is ``None``,
        in which case the XML predefined directory format is used.

    xml_path : str
        Path to the directory containing the XML files. The default is ``None``,
        in which case the XML predefined directory format is used.

    Returns
    -------
    graphic_path : str
        Path of the directory containing the graphics.

    link_path : str
        Path of the directory containing the links.

    term_path : str
        Path of the directory containing the terms.

    xml_path : str
        Path of the directory containing the XML files.

    """

    if graph_path is None:
        graph_path = os.path.join(path, "graphics")
        if not os.path.isdir(graph_path):
            print(
                f"WARNING: the path {graph_path} does not exist. Follow the predefined format or enter the graphic path manually."  # noqa : E501
            )

    if link_path is None:
        link_path = os.path.join(path, "links")
        if not os.path.isdir(link_path):
            print(
                f"WARNING: the path {link_path} does not exist. Follow the predefined format or enter the link path manually."  # noqa : E501
            )

    if term_path is None:
        term_path = os.path.join(path, "terms")
        if not os.path.isdir(term_path):
            print(
                f"WARNING: the path {term_path} does not exist. Follow the predefined format or enter the term path manually."  # noqa : E501
            )

    if xml_path is None:
        xml_path = os.path.join(path, "xml")
        if not os.path.isdir(xml_path):
            print(
                f"WARNING: the path {xml_path} does not exist. Follow the predefined format or enter the XML path manually."  # noqa : E501
            )

    return graph_path, link_path, term_path, xml_path

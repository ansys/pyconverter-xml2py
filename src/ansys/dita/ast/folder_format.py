import argparse
import os

# Pre-defined directory format

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
    It is advised to follow the pre-defined directory structure.

    Parameters
    ----------
    path: str
        If path is None, the path is set with the argument parser `-p` or `--xml-path`,
        or with the XML_PATH environment variable.

    Return
    ------
    path: str
        Path of the XML documentation to be converted.

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
    """Return the path to the directory containing the graphics.

    Parameters
    ----------
    path : strg
        Path to the directory with the pre-defined format .

    graph_path : strg
        If not following the XML pre-defined directory format, specify the path to the directory
        containing the graphics.

    link_path : strg
        If not following the XML pre-defined directory format, specify the path to the directory
        containing the links.

    term_path : strg
        If not following the XML pre-defined directory format, specify the path to the directory
        containing the terms

    xml_path : strg
        If not following the XML pre-defined directory format, specify the path to the directory
        containing the xml.

    Returns
    -------
    graphic_path : str
        Path of the directory containing the graphics.

    link_path : str
        Path of the directory containing the links.

    term_path : str
        Path of the directory containing the terms.

    xml_path : str
        Path of the directory containing the xml.

    """

    if graph_path is None:
        graph_path = os.path.join(path, "graphics")
        if not os.path.isdir(graph_path):
            print(
                f"WARNING: the path {graph_path} does not exits. Please follow the pre-defined format or enter the graphic path manually."  # noqa : E501
            )

    if link_path is None:
        link_path = os.path.join(path, "links")
        if not os.path.isdir(link_path):
            print(
                f"WARNING: the path {link_path} does not exits. Please follow the pre-defined format or enter the link path manually."  # noqa : E501
            )

    if term_path is None:
        term_path = os.path.join(path, "terms")
        if not os.path.isdir(term_path):
            print(
                f"WARNING: the path {term_path} does not exits. Please follow the pre-defined format or enter the term path manually."  # noqa : E501
            )

    if xml_path is None:
        xml_path = os.path.join(path, "xml")
        if not os.path.isdir(xml_path):
            print(
                f"WARNING: the path {xml_path} does not exits. Please follow the pre-defined format or enter the xml path manually."  # noqa : E501
            )

    return graph_path, link_path, term_path, xml_path

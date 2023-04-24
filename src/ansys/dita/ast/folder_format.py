import argparse
import os

# Pre-defined folder format

# XML_folder
# |
# | graphics
# |   | images
# |   | gifs
# |   | other format
# |   |
# |
# | links
# |   | .db files
# |   |
# |
# | terms
# |   | glb
# |   | | docu_global.ent
# |   | | build_variables.ent
# |   | | manual_name               # this file name can be modified
# |   | |
# |   | ent
# |   | | .ent files
# |   | |
# |   |
# |
# | books
# |   | .ent files
# |   | .xml files
# |   | com_subfolders
# |   |   | .xml files
# |   |   | mathgraphics_folder
# |   |   |   | .svg files
# |   |   |   |
# |   |   |
# |   |
# |


def xml_path(path=None):
    """Return the path to the folder containing the XML documentation.
    It is advised to follow the pre-defined folder structure.

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

        parser = argparse.ArgumentParser()
        parser.add_argument("--xml-path", "-p", help="XML Documentation path")

        args = parser.parse_args()

        path = args.xml_path
        if path is None:
            path = os.environ.get("XML_PATH")
        if path is None:
            raise RuntimeError(
                "Missing the XML documentation path. Specify this with either --xml-path, -p, or set the XML_PATH environment variable"  # noqa : E501
            )

        path = os.path.abspath(os.path.expanduser(path))

    # Verification
    if not os.path.isdir(path):
        raise FileNotFoundError(f"Documentation path at {path} does not exist")

    return path


def get_paths(xml_path, graph_path=None, link_path=None, term_path=None, book_path=None):
    """Return the path to the folder containing the graphics.

    Parameters
    ----------
    xml_path : strg
    Path to the XML folder that will be converted.

    graph_path : strg
    If not following the XML pre-defined folder format, specify the path to the folder containing
    the graphics.

    link_path : strg
    If not following the XML pre-defined folder format, specify the path to the folder containing
    the links.

    term_path : strg
    If not following the XML pre-defined folder format, specify the path to the folder containing
    the terms

    book_path : strg
    If not following the XML pre-defined folder format, specify the path to the folder containing
    the books.

    Returns
    -------
    graphic_path : str
    Path of the folder containing the graphics.

    link_path : str
    Path of the folder containing the links.

    term_path : str
    Path of the folder containing the terms.

    book_path : str
    Path of the folder containing the books.

    """

    if graph_path is None:
        graph_path = os.path.join(xml_path, "graphics")
        if not os.path.isdir(graph_path):
            print(
                f"WARNING: the path {graph_path} does not exits. Please follow the pre-defined format or enter the graphic path manually."  # noqa : E501
            )

    if link_path is None:
        link_path = os.path.join(xml_path, "links")
        if not os.path.isdir(link_path):
            print(
                f"WARNING: the path {link_path} does not exits. Please follow the pre-defined format or enter the link path manually."  # noqa : E501
            )

    if term_path is None:
        term_path = os.path.join(xml_path, "terms")
        if not os.path.isdir(term_path):
            print(
                f"WARNING: the path {term_path} does not exits. Please follow the pre-defined format or enter the term path manually."  # noqa : E501
            )

    if book_path is None:
        book_path = os.path.join(xml_path, "books")
        if not os.path.isdir(book_path):
            print(
                f"WARNING: the path {book_path} does not exits. Please follow the pre-defined format or enter the book path manually."  # noqa : E501
            )

    return graph_path, link_path, term_path, book_path

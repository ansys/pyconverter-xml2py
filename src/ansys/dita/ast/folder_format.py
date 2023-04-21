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
# |   | .ent files
# |   |
# |
# | commands
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
    # Declaration
    if path is None:

        parser = argparse.ArgumentParser()
        parser.add_argument("--xml-path", "-p", help="XML Documentation path")

        args = parser.parse_args()

        path = args.xml_path
        if path is None:
            path = os.environ.get("XML_PATH")
        if path is None:
            raise RuntimeError(
                "Missing the XML documentation path. Specify this with either --xml-path or set the XML_PATH environment variable"  # noqa : E501
            )

        path = os.path.abspath(os.path.expanduser(path))

    # Verification
    if not os.path.isdir(path):
        raise FileNotFoundError(f"Documentation path at {path} does not exist")

    return path


def graphic_path(xml_path, path=None):
    """Return the path to the folder containing the graphics.

    Parameters
    ----------
    xml_path : strg
    Path to the XML folder that will be converted.

    path : strg
    If not following the XML pre-defined folder format, specify the path to the folder containing
    the graphics.

    Returns
    -------
    graphic_path : str
    Return the folder containing the graphics.
    """

    if path is None:
        graphic_path = os.path.join(xml_path, "graphics")

    else:
        graphic_path = path

    return graphic_path


def link_path(xml_path, path=None):
    """Return the path to the folder containing the links.

    Parameters
    ----------
    xml_path : strg
    Path to the XML folder that will be converted.

    path : strg
    If not following the XML pre-defined folder format, specify the path to the folder containing
    the links.

    Returns
    -------
    link_path : str
    Return the folder containing the links.
    """

    if path is None:
        link_path = os.path.join(xml_path, "links")

    else:
        link_path = path

    return link_path


def term_path(xml_path, path=None):
    """Return the path to the folder containing the terms.

    Parameters
    ----------
    xml_path : strg
    Path to the XML folder that will be converted.

    path : strg
    If not following the XML pre-defined folder format, specify the path to the folder containing
    the terms.

    Returns
    -------
    term_path : str
    Return the folder containing the terms.
    """

    if path is None:
        term_path = os.path.join(xml_path, "terms")

    else:
        term_path = path

    return term_path


def book_path(xml_path, path=None):
    """Return the path to the folder containing the books.

    Parameters
    ----------
    xml_path : strg
    Path to the XML folder that will be converted.

    path : strg
    If not following the XML pre-defined folder format, specify the path to the folder containing
    the books.

    Returns
    -------
    book_path : str
    Return the folder containing the books.
    """

    if path is None:
        book_path = os.path.join(xml_path, "books")

    else:
        book_path = path

    return book_path

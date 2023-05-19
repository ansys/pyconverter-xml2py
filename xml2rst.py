from pydita_ast import writer as wr

"""
Parse MAPDL command XML documentation.

"""
import argparse
import os

# from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--xml-path", "-p", help="Documentation path")
    # not accepted
    # parser.add_argument("--command", help="Convert a single command")
    parser.add_argument("--no-clean", help="Do not remove the existing package directory")
    parser.add_argument("--no_docs", action="store_true", help="Do not write to tinypages")
    args = parser.parse_args()

    directory_path = args.xml_path
    if directory_path is None:
        directory_path = os.environ.get("XML_PATH")
    if directory_path is None:
        raise RuntimeError(
            "Missing the XML documentation path. Specify this with either --xml-path, -p, or set the XML_PATH environment variable"  # noqa : E501
        )

    directory_path = os.path.abspath(os.path.expanduser(directory_path))
    cur_path = os.getcwd()

    # Verification
    if not os.path.isdir(directory_path):
        raise FileNotFoundError(f"Documentation path at {directory_path} does not exist")

    commands = wr.convert(directory_path)
    cmd_path = wr.write_source(commands, directory_path, cur_path)
    doc_src = wr.write_docs(commands, cur_path)

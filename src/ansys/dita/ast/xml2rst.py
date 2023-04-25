from ansys.dita.ast import folder_format as path
from ansys.dita.ast import load_xml_doc as load

"""
Parse MAPDL command XML documentation.

"""
import argparse
import os

# from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--xml-path", "-p", help="Ansys Documentation path")
    # not accepted
    # parser.add_argument("--command", help="Convert a single command")
    parser.add_argument("--no-clean", help="Do not remove the existing package directory")
    parser.add_argument("--no_docs", action="store_true", help="Do not write to tinypages")
    args = parser.parse_args()

    xml_path = args.xml_path
    if xml_path is None:
        xml_path = os.environ.get("XML_PATH")
    if xml_path is None:
        raise RuntimeError(
            "Missing the XML documentation path. Specify this with either --xml-path, -p, or set the XML_PATH environment variable"  # noqa : E501
        )

    xml_path = os.path.abspath(os.path.expanduser(xml_path))
    conv_path = os.getcwd()

    # Verification
    if not os.path.isdir(xml_path):
        raise FileNotFoundError(f"Documentation path at {xml_path} does not exist")

    graph_path, link_path, term_path, xml_path = path.get_paths(xml_path)

    links = load.load_links(link_path)
    fcache = load.load_fcache(graph_path)
    docu_global = load.load_docu_global(term_path)
    terms, version_variables = load.load_terms(term_path, docu_global, links, fcache)

    # chap2.write_chapt2(doc_path, conv_path, links, base_url)

    # commands = conv.convert(doc_path)
    # cmd_path = conv.write_source(commands, conv_path)
    # doc_src = conv.write_docs(commands, conv_path)

# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pyconverter.xml2py.load_xml_doc as lxd


def test_load_links(link_path):
    links = lxd.load_links(link_path)
    assert links["ds_Support_Types"] == (
        "wb_sim",
        "",
        "ds_Elastic_Support.html",
        "Support Type Boundary Conditions",
    )


def test_load_fcache(graph_path):
    fcache = lxd.load_fcache(graph_path)
    assert fcache["gcmdrsymm4"] == "gcmdrsymm4.png"


def test_load_docu_global(term_path):
    docu_global = lxd.load_docu_global(term_path)
    assert docu_global["acpmdug"] == ("acp_md", "acp_md", "&bk_acp_md;")


def test_load_terms(load_terms):
    terms, version_variables = load_terms
    assert terms["me"] == "Ansys Mechanical"
    assert version_variables.autogenerated_directory_name == "pyconverter.generatedcommands"
    assert version_variables.version == terms["ansys_internal_version"]

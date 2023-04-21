import os

import pytest

import ansys.dita.ast.xml_ast as ast

# @pytest.fixture
# def doc_path(ghdir):
#     doc_path = os.path.join(ghdir, "mapdl-cmd-doc")
#     return doc_path


# ##########################################################+
# ##########################################################
# # To run the Unit Tests locally
# ##########################################################
# ##########################################################


# @pytest.fixture
# def doc_path():
#     return "D:/repos/pyansys/mapdl-cmd-doc23.1"


# ##########################################################
# ##########################################################


@pytest.fixture
def glb_path(doc_path):
    glb_path, _ = ast.create_glb_cmd_path(doc_path)
    return glb_path


@pytest.fixture
def cmd_path(doc_path):
    _, cmd_path = ast.create_glb_cmd_path(doc_path)
    return cmd_path


@pytest.fixture
def grph_pth(cmd_path, doc_path):
    grph_pth = ast.create_grph_pth(cmd_path, doc_path)
    return grph_pth


@pytest.fixture
def GLB_VAL(glb_path):
    GLB_VAL = ast.create_GLB_VAL(glb_path)
    return GLB_VAL


@pytest.fixture
def fcache(grph_pth, GLB_VAL):
    fcache = ast.load_graphics_fcache(grph_pth)
    return fcache


@pytest.fixture
def docu_global(glb_path):
    docu_global = ast.create_docu_global(glb_path)
    return docu_global


@pytest.fixture
def terms_global(GLB_VAL, glb_path):
    terms_global = ast.create_terms_global(GLB_VAL, glb_path)
    return terms_global


@pytest.fixture
def links(glb_path):
    links = ast.get_links(glb_path)
    return links


@pytest.fixture
def base_url(GLB_VAL):
    _, _, base_url, _ = ast.variables(GLB_VAL)
    return base_url


def test_create_doc_path(doc_path):
    doc_path_from_ast = ast.create_doc_path(doc_path)
    assert doc_path == doc_path_from_ast


def test_create_glb_cmd_path(doc_path):
    glb_path, cmd_path = ast.create_glb_cmd_path(doc_path)
    assert glb_path == os.path.join(doc_path, "global")
    assert cmd_path == os.path.join(doc_path, "docu_files/ans_cmd")


def test_create_grph_pth(cmd_path, doc_path):
    grph_pth = ast.create_grph_pth(cmd_path, doc_path)
    assert grph_pth == os.path.join(cmd_path, "graphics")


def test_create_GLB_VAL(glb_path):
    GLB_VAL = ast.create_GLB_VAL(glb_path)
    assert GLB_VAL["copymonth"] == "July"


def test_load_graphics_fcache(grph_pth, GLB_VAL):
    fcache = ast.load_graphics_fcache(grph_pth)
    assert fcache["gcmdrsymm4"] == "gcmdrsymm4.png"


def test_create_docu_global(glb_path):
    docu_global = ast.create_docu_global(glb_path)
    assert docu_global["acpmdug"] == ("acp_md", "acp_md", "bk_acp_md")


def test_create_terms_global(GLB_VAL, glb_path):
    terms_global = ast.create_terms_global(GLB_VAL, glb_path)
    assert terms_global["pip"] == "Product Improvement Program"


def test_get_links(glb_path):
    links = ast.get_links(glb_path)
    assert links["ds_Support_Types"] == (
        "wb_sim",
        "",
        "ds_Elastic_Support.html",
        "Support Type Boundary Conditions",
    )


def test_variables(GLB_VAL):
    PYMAPDL_CLASS, ans_version, base_url, cmd_base_url = ast.variables(GLB_VAL)
    assert PYMAPDL_CLASS == "ansys.mapdl.generatedcommands"
    assert ans_version == GLB_VAL["ansys_internal_version"]
    assert base_url == f"https://ansyshelp.ansys.com/Views/Secured/corp/v{ans_version}/en/"
    assert cmd_base_url == f"{base_url}/ans_cmd/"


def test_load_ansys_manuals(glb_path, docu_global, links, base_url, terms_global):
    terms_global = ast.load_ansys_manuals(
        glb_path, docu_global, links, base_url, fcache, terms_global
    )
    assert terms_global["me"] == "Ansys Mechanical"


def test_get_parser():
    parser = ast.get_parser()
    assert parser["tgroup"] == ast.TGroup

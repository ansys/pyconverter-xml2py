# import os

import ansys.dita.ast.ast_tree as ast
from lxml.html import fromstring
import pytest


@pytest.mark.parametrize(
    "command",
    ["/PREP7", "*DMAT", "SORT"],
)
def test_py_name(command):
    pycommand = ast.to_py_name(command)
    if command == "/PREP7":
        assert pycommand == "prep7"
    elif command == "*DMAT":
        assert pycommand == "dmat"
    elif command == "SORT":
        assert pycommand == "sort"
    else:
        raise ValueError("Invalid pytest command parameter.")


@pytest.fixture
def alpha_text():
    return "This is a test."


def test_trail_alpha(alpha_text):
    alpha = "This is a test."
    split_alpha = ast.split_trail_alpha(alpha_text)
    assert split_alpha == ("This ", "is a test.")


@pytest.mark.parametrize(
    "numeric_string",
    ["2804", "28.04", "TEA"],
)
def test_is_numeric(numeric_string):
    is_num = ast.is_numeric(numeric_string)
    if numeric_string == "2804":
        assert is_num is True
    elif numeric_string == "28.04":
        assert is_num is True
    elif numeric_string == "TEA":
        assert is_num is False
    else:
        raise ValueError("Invalid pytest command parameter.")


@pytest.fixture
def str_element():
    return "<element extra_value='0000'>element test</element>"


@pytest.fixture
def element(str_element):
    element = fromstring(str_element)
    return element


def test_init_Element(element):
    elem = ast.Element(element)
    assert elem._element == element
    assert elem._content == ["element test"]


def test_parse_element(element):
    element_parser = ast.parse_element(element)
    ast_element = ast.Element(element)
    assert len(element_parser) == len(ast_element)
    assert type(element_parser) == type(ast_element)
    assert element_parser._element == ast_element._element
    assert element_parser._content == ast_element._content


@pytest.fixture
def str_element_with_children():
    return '<element extra_value="0000">element test with children <child>child 1</child> <child>child 2</child> <child>child 3</child></element>'  # noqa : E501


@pytest.fixture
def element_with_children(str_element_with_children):
    element_with_children = fromstring(str_element_with_children)
    return element_with_children


@pytest.fixture
def Element_with_children(element_with_children):
    return ast.Element(element_with_children)


def test_parse_children(element_with_children):
    parser = ast.parse_children(element_with_children)
    from_string = element_with_children.getchildren()
    assert parser == from_string


def test_init_Element_with_children(element_with_children, Element_with_children):
    assert Element_with_children._element == element_with_children
    assert len(Element_with_children._content) == 4


def test_Element_text_content(Element_with_children):
    content = Element_with_children.text_content
    assert content == "element test with children child 1 child 2 child 3"


def test_Element_raw(str_element_with_children, Element_with_children):
    raw = Element_with_children.raw
    assert raw == str_element_with_children

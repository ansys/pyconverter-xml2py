# import argparse
# import glob
import logging

# import os
# from pathlib import Path
import re
import textwrap

# import unicodedata
import warnings

# from lxml.etree import ParserError, tostring
from lxml.etree import tostring
from lxml.html import fromstring

# from tqdm import tqdm

CONV_EQN = False
SUPPORT_TABLES = True

if CONV_EQN:
    from py_asciimath.translator.translator import MathML2Tex
    from pylatexenc.latex2text import LatexNodes2Text
else:
    pass

logging.getLogger("py_asciimath.utils").setLevel("CRITICAL")


# common statements used within the docs to avoid duplication
CONST = {
    # "&thetas;": "θ",  # consider replacing with :math:`\theta`
    "Dtl?": "",
    "Caret?": "",
    "Caret1?": "",
    "Caret 40?": "",
    '``"``': "``",
}

CLEANUP = {
    ",, ": ", ",
    ", , ": ", ",
    ",. ": ". ",
    " , ": ", ",
    ", )": ")",
    ",)": ")",
    "% ``": "``%",  # Ansys variable names should be pulled inside literals
    "`` %": "%``",  # same
}

# map APDL command to pymapdl function
CMD_MAP = {}

# APDL commands to skip
SKIP = {"*IF", "*ELSE", "C***", "*RETURN"}


# def nested_exec(text):
#     """Nested execute."""
#     exec(text)


def to_py_name(name):
    """Convert to a python compatible name."""
    name = CMD_MAP.get(name, name.lower())
    return re.sub(r"[^a-z0-9]", "", name)


# ############################################################################
# # Dita_AST functions
# ############################################################################


def multireplace(string, replacements, ignore_case=False):
    """Given a string and a replacement map, it returns the replaced string.

    Parameters
    ----------
    string : str
        String to execute replacements on

    replacements : dict
        Replacement dictionary {value to find: value to replace}.

    ignore_case : bool
        Whether the match should be case insensitive

    Returns
    -------
    str
    """
    if not replacements:
        # Edge case that'd produce a funny regex and cause a KeyError
        return string

    # If case insensitive, we need to normalize the old string so that later a replacement
    # can be found. For instance with {"HEY": "lol"} we should match and find a replacement for
    # "hey", "HEY", "hEy", etc.
    if ignore_case:

        def normalize_old(s):
            return s.lower()

        re_mode = re.IGNORECASE

    else:

        def normalize_old(s):
            return s

        re_mode = 0

    replacements = {normalize_old(key): val for key, val in replacements.items()}

    # Place longer ones first to keep shorter substrings from matching where the longer ones
    # should take place
    # For instance given the replacements {'ab': 'AB', 'abc': 'ABC'} against the string 'hey abc',
    # it should produce 'hey ABC' and not 'hey ABc'
    rep_sorted = sorted(replacements, key=len, reverse=True)
    rep_escaped = map(re.escape, rep_sorted)

    # Create a big OR regex that matches any of the substrings to replace
    pattern = re.compile("|".join(rep_escaped), re_mode)

    # For each match, look up the new string in the replacements, being the key the normalized
    # old string
    return pattern.sub(lambda match: replacements[normalize_old(match.group(0))], string)


def split_trail_alpha(text):
    """Split a string based on the last tailing non alphanumeric character."""
    for ii, char in enumerate(text):
        if not char.isalnum():
            break

    ii += 1

    return text[:ii], text[ii:]


def is_numeric(text):
    """Return True when a string is numeric."""
    try:
        float(text)
        return True
    except ValueError:
        return False


class Element:
    """Base element."""

    def __init__(self, element, parse_children=True):
        self._element = element
        self._content = []

        if element.text is not None:
            content = " ".join(element.text.split())
            if content:
                self._content.append(content)
        if parse_children:
            for child in element.getchildren():
                self._content.append(parse_element(child))
        if element.tail is not None:
            text = " ".join(element.tail.split())
            if text:
                self._content.append(text)

    @property
    def text_content(self):
        """Return the text content."""
        return self._element.text_content()

    @property
    def raw(self):
        """Return the raw string of the element."""
        return tostring(self._element).decode()

    @property
    def tostring(self):
        """Return the attributes of the element as a dictionnary."""
        return tostring(self._element)

    def has_children(self):
        return bool(len(self._element.getchildren()))

    def get(self, entry):
        """Get an item from an element."""
        return self._element.get(entry)

    @property
    def added(self):
        """Has the revision flag "added"."""
        return self.get("revisionflag") == "added"

    @property
    def any_isalnum(self):
        """Return True if any characters are alpha numeric."""
        return any([char.isalnum() for char in str(self)])

    @property
    def tail(self):
        return " ".join([str(item) for item in self._content[1:]])

    def print_tree(self):
        """Print the tree."""
        print(self.types_repr())

    def types_repr(self):
        """Return the string types."""
        return "\n".join([str(type(item)) for item in self])

    def __getitem__(self, index):
        return self._content[index]

    def __len__(self):
        return len(self._content)

    @property
    def children(self):
        """Children of the tree."""
        return self._content

    @property
    def title(self):
        """Return the element title."""
        return self.find("Title")

    @property
    def content(self):
        """Return text content."""
        return self._content

    def __repr__(self):
        return "".join([str(item) for item in self._content])

    @property
    def id(self):
        return self._element.get("id")

    def to_rst(self, prefix="", links=None, base_url=None, fcache=None):
        items = []
        for item in self:
            if isinstance(item, Element):
                if item.tag in item_needing_all:
                    items.append(
                        item.to_rst(
                            prefix,
                            links=links,
                            base_url=base_url,
                            fcache=fcache,
                        )
                    )
                elif item.tag in item_needing_links_base_url:
                    items.append(item.to_rst(prefix, links=links, base_url=base_url))
                elif item.tag in item_needing_fcache:
                    items.append(item.to_rst(prefix=prefix, fcache=fcache))
                else:
                    items.append(item.to_rst(prefix=prefix))
            else:
                items.append(prefix + str(item))
        return " ".join(items)

    def rec_find(self, _type, terms_global=None):
        """Return the first type matching a given type string recursively."""
        for item in self:
            if type(item).__name__ == _type:
                if _type == "Refname" or _type == "Refnamediv":
                    item.terms_global = terms_global
                return item
            if isinstance(item, Element):
                subitem = item.rec_find(_type)
                if subitem is not None:
                    return subitem
        return None

    def find(self, _type, terms_global=None):
        """Return the first type matching a given type string."""
        for item in self:
            if type(item).__name__ == _type:
                if _type == "Refname" or _type == "Refnamediv":
                    if terms_global == None:
                        print("ERROR: terms_global not defined for a Refname class")
                    item.terms_global = terms_global
                return item
        return None

    def find_all(self, _type, recursive=False, terms_global=None):
        """Return all types matching a given type string."""
        items = []
        for item in self:
            if type(item).__name__ == _type:
                if _type == "Refname" or _type == "Refnamediv":
                    item.terms_global = terms_global
                items.append(item)
            elif recursive and isinstance(item, Element):
                items.extend(item.find_all(_type))

        return items

    @property
    def next_elem(self):
        """Return the next element."""
        elem = self._element.getnext()
        return parse_element(elem) if elem is not None else elem

    @property
    def prev_elem(self):
        """Return the previous element."""
        elem = self._element.getprevious()
        return parse_element(elem) if elem is not None else elem

    @property
    def tag(self):
        """Element tag."""
        return self._element.tag


class ItemizedList(Element):
    """ItemizedList element."""

    def __repr__(self):
        return "\n".join([f"* {str(item).strip()}" for item in self])

    def to_rst(self, prefix="", links=None, base_url=None, fcache=None):
        lines = []
        for item in self:
            if isinstance(item, Element):
                if item.tag in item_needing_all:
                    item_lines = item.to_rst(
                        prefix, links=links, base_url=base_url, fcache=fcache
                    ).splitlines()
                elif item.tag in item_needing_links_base_url:
                    item_lines = item.to_rst(prefix, links=links, base_url=base_url).splitlines()
                elif item.tag in item_needing_fcache:
                    item_lines = item.to_rst(prefix=prefix, fcache=fcache).splitlines()
                else:
                    item_lines = item.to_rst(prefix)
            else:
                item_lines = str(item).splitlines()

            if item_lines and isinstance(item, Member):
                line = (
                    item_lines[0].to_rst()
                    if isinstance(item_lines, Element)
                    else str(item_lines[0])
                )
                lines.append(textwrap.indent(line, prefix + "* "))
                for line in item_lines[1:]:
                    text = line.to_rst(prefix) if isinstance(line, Element) else str(line)
                    lines.append(textwrap.indent(text, prefix + "  "))
            else:
                lines.extend(item_lines)

        # lists must have at least one line proceeding
        lines = ["", ""] + lines + [""]
        return "\n".join(lines)


class SimpleList(ItemizedList):
    """ItemizedList element."""

    def __repr__(self):
        return "\n".join([f"* {str(item).strip()}" for item in self])


class Member(Element):
    """Simple list member element."""

    pass

    # def to_rst(self, prefix=''):
    #     text = super().to_rst(prefix)
    #     return text.replace('\n', '')

    # def to_rst(self, prefix=""):
    #     items = []
    #     for item in self:
    #         if isinstance(item, Element):
    #             items.append(item.to_rst(prefix))
    #         else:
    #             items.append(str(item))
    #     return " ".join(items)


class OrderedList(Element):
    """Ordered list element."""

    def to_rst(self, prefix="", links=None, base_url=None):
        prefix += "    "
        ordered_list = []
        for item in self:
            if item.tag in item_needing_links_base_url:
                rst_item = item.to_rst(prefix, links=links, base_url=base_url)
            else:
                rst_item = item.to_rst(prefix)
            ordered_list.append(rst_item)
        return "\n".join(ordered_list)


class ListItem(Element):
    """List item element."""

    def to_rst(self, prefix="", links=None, base_url=None, fcache=None):
        items = []
        for item in self:
            if isinstance(item, Element):
                if item.tag in item_needing_all:
                    items.append(
                        item.to_rst(
                            prefix,
                            links=links,
                            base_url=base_url,
                            fcache=fcache,
                        )
                    )
                elif item.tag in item_needing_links_base_url:
                    items.append(item.to_rst(prefix, links=links, base_url=base_url))
                elif item.tag in item_needing_fcache:
                    items.append(item.to_rst(prefix=prefix, fcache=fcache))
                else:
                    items.append(item.to_rst(prefix))
            else:
                items.append(str(item))
        return "\n".join(items)


class FileName(Element):
    """Filename element."""

    def to_rst(self, prefix=""):
        return f"``{self[0]}`` {self.tail}"


class OLink(Element):
    def __init__(self, element):
        super().__init__(element)

    @property
    def targetptr(self):
        return self.get("targetptr")

    @property
    def targetdoc(self):
        return self.get("targetdoc")

    def to_rst(self, prefix="", links=None, base_url=None):
        key = f"{self.targetptr}"
        if (links or base_url) is None:
            print("ERROR in the links or the base_url definitions - OLink class.")
        if key in links:
            root_name, root_title, href, text = links[key]
            link = f"{base_url}{root_name}/{href}"
            content = self.text_content
            content = content.replace("\n", "")
            content = content.replace("\r", "")
            while "  " in content:
                content = content.replace("  ", " ")
            if len(content) > 1 and content[0] == "":
                content = content[1:]
            content = text if content == "" else content
            content = content.strip()
            tail = self.tail
            tail = tail.replace("\n", "")
            tail = tail.replace("\r", "")
            return f"`{content} <{link}>`_ {self.tail}"
        # else:
        #     print(self.targetptr)

        return super().to_rst(prefix)


class Paragraph(Element):
    """Paragraph element."""

    def __repr__(self):
        lines = [""]
        lines.append(" ".join([str(item) for item in self._content]))
        lines.append("\n")
        return "".join(lines)

    def to_rst(self, prefix="", links=None, base_url=None, fcache=None):
        """Convert to RST style."""
        items = []
        for item in self:
            if isinstance(item, Element):
                if isinstance(item, Variablelist):
                    items.append(
                        "\n\n"
                        + item.to_rst(
                            prefix=prefix,
                            links=links,
                            base_url=base_url,
                            fcache=fcache,
                        )
                    )
                else:
                    if item.tag in item_needing_all:
                        items.append(
                            item.to_rst(
                                prefix=prefix,
                                links=links,
                                base_url=base_url,
                                fcache=fcache,
                            )
                        )
                    elif item.tag in item_needing_links_base_url:
                        items.append(item.to_rst(prefix=prefix, links=links, base_url=base_url))
                    elif item.tag in item_needing_fcache:
                        items.append(item.to_rst(prefix=prefix, fcache=fcache))
                    else:
                        items.append(item.to_rst(prefix=prefix))
            else:
                items.append(str(item))

        # if len(items) > 1:
        #     spaced_items = []
        #     for item in items:
        #         if not item.startswith('\n'):
        #             spaced_items.append(' ' + item)
        #         else:
        #             spaced_items.append(item)
        # else:
        #     spaced_items = items

        return " ".join(items) + "\n"


class Phrase(Element):
    """Phrase element."""

    def __repr__(self):
        return " ".join([str(item) for item in self._content])


class Structname(Element):
    """Structname element."""


class Title(Element):
    def __repr__(self):
        return " ".join([str(item) for item in self._content]) + "\n"


class Emphasis(Element):
    """Emphasis element."""

    @property
    def role(self):
        return self._element.get("role")

    def to_rst(self, prefix="", links=None, base_url=None):

        if self.role == "bold":
            # TODO: this isn't the correct way of making text bold
            content = f"{self[0]} "
        elif self.role == "italic":
            # TODO: this isn't the correct way of making text itallic
            content = f"`{self[0]}` "
        # elif self.role == 'var':
        # content = f"``{self[0]}`` "
        else:
            content = f"{self[0]} "

        items = []
        for item in self[1:]:
            if isinstance(item, Element):
                if item.tag in item_needing_links_base_url:
                    items.append(item.to_rst(prefix, links=links, base_url=base_url))
                else:
                    items.append(item.to_rst(prefix))
            else:
                items.append(str(item))

        return content + " ".join(items)


class Example(Element):
    """Example element."""

    # def source(self):
    #     """The program listing of the documentation."""
    #     for item in self._content:
    #         if isinstance(item, ProgramListing):
    #             return item
    #     return ""
    pass


class InformalExample(Element):
    """Example element."""

    def __repr__(self):
        lines = ["\n"]
        if self.title:
            lines.append(f"Example:\n")
        else:
            lines.append(f"Example: {self.title}\n")
        lines.extend([f"{line}" for line in self._content])  # self._content.splitlines()
        return "\n".join(lines)


class GuiMenu(Element):
    """GUI Menu element."""

    pass


class Replaceable(Element):
    """Replaceable element."""

    @property
    def is_equals(self):
        """Replaceable equals something."""
        # return self.tail.startswith("=")
        return False

    @property
    def content_equals(self):
        words = self.tail.split("=")[1].split()
        if not words:
            # probably a literal
            next_elem = self.next_elem
            parm = next_elem[0]
            next_elem.content[0] = ""
        else:
            parm = words[0]

        if len(words) > 1:
            tail = " ".join(words[1:])
        else:
            tail = ""
        if parm.startswith('"'):
            # quoted parm
            ii = parm[1:].find('"') + 2
            parm, extra = parm[:ii], parm[ii:]
        else:
            parm, extra = split_trail_alpha(parm)
        tail = f"{extra} {tail}"

        if not is_numeric(parm) and not parm.startswith('"'):
            parm = f'"{parm}"'

        return f"``{self.content[0].lower()}={parm}`` {tail}"

    def to_rst(self, prefix=""):
        """Convert to an rst format."""
        if isinstance(self.prev_elem, Command):
            if any([self.content[0] in arg for arg in self.prev_elem.args]):
                return f"{self.tail}"
        if self.is_equals:
            return self.content_equals
        return f"``{self.content[0]}`` {self.tail}"


class ProgramListing(Element):
    """Program listing element."""

    @property
    def source(self):
        if self._element.text is None:
            return "\n".join(str(item) for item in self.content)
        return self._element.text

    def to_rst(self, prefix=""):
        header = f"\n\n{prefix}.. code::\n\n"
        return header + textwrap.indent(self.source, prefix + " " * 3) + "\n"


class Variablelist(Element):
    """Variable list."""

    def to_rst(self, prefix="", links=None, base_url=None, fcache=None):
        active_items = []
        for item in self:
            if isinstance(item, VarlistEntry) and not item.active:
                continue
            if isinstance(item, Element):
                if item.tag in item_needing_all:
                    active_items.append(
                        item.to_rst(
                            prefix,
                            links=links,
                            base_url=base_url,
                            fcache=fcache,
                        )
                    )
                elif item.tag in item_needing_links_base_url:
                    active_items.append(item.to_rst(prefix, links=links, base_url=base_url))
                elif item.tag in item_needing_fcache:
                    active_items.append(item.to_rst(prefix=prefix, fcache=fcache))
                else:
                    active_items.append(item.to_rst(prefix))
            else:
                active_items.append(str(item))
        return "\n".join(active_items) + "\n"

    @property
    def terms(self):
        return [str(item.term) for item in self if isinstance(item, VarlistEntry)]


class RefSection(Element):
    """Reference Section element."""

    def to_rst(self, prefix="", links=None, base_url=None, fcache=None):
        """Convert to restructured text."""
        items = []
        for item in self[1:]:
            if isinstance(item, Element):
                if item.tag in item_needing_all:
                    items.append(
                        item.to_rst(
                            prefix=prefix,
                            links=links,
                            base_url=base_url,
                            fcache=fcache,
                        )
                    )
                elif item.tag in item_needing_links_base_url:
                    items.append(item.to_rst(prefix=prefix, links=links, base_url=base_url))
                elif item.tag in item_needing_fcache:
                    items.append(item.to_rst(prefix=prefix, fcache=fcache))
                else:
                    items.append(item.to_rst(prefix=prefix))
            else:
                items.append(str(item))
        return "\n".join(items)


class VarlistEntry(Element):
    """Variable list entry."""

    @property
    def parm_types(self):
        """Return the parameter type(s).

        This is guessed from any subvarlists. If unavailable, then it's guessed
        from the description of the variable.

        This is either a string, float, or int (or some combination thereof).

        """
        varlist = self.rec_find("Variablelist")

        parm_types = [str]
        if varlist is not None:
            terms = varlist.terms
            if terms:
                terms_numeric = [is_numeric(term) for term in terms]
                if all(terms_numeric):
                    parm_types = [int]
                elif any(terms_numeric):
                    parm_types = [int, str]
                else:
                    parm_types = [str]

                # consider checking for bool
                # terms_numeric = set(terms) == set(['1', '0'])

        return parm_types

    @property
    def term(self):
        return self.content[0]

    @property
    def text(self):
        return self.content[1]

    def py_term(self, links=None, base_url=None):
        """Python compatible term."""
        if self.is_arg:
            arg = str(self.term).lower()

            if arg == "type":
                arg = "type_"

            if self.parm_types is not None:
                ptype_str = " or ".join([parm_type.__name__ for parm_type in self.parm_types])

                return f"{arg} : {ptype_str}"
            return f"{arg}"

        # if self.term.tag in item_needing_all:
        #     arg = self.term.to_rst(links=links, base_url=base_url, fcache=fcache).replace("--", "").strip() # noqa : E501
        if self.term.tag in item_needing_links_base_url:
            arg = self.term.to_rst(links=links, base_url=base_url).replace("--", "").strip()
        # elif self.term.tag in item_needing_fcache:
        #     arg = self.term.to_rst(fcache=fcache).replace("--", "").strip()
        else:
            arg = self.term.to_rst().replace("--", "").strip()

        # sanity check
        if "blank" in arg.lower():
            arg = ""

        if not is_numeric(arg):
            return f'"{arg}"'
        return arg

    def __repr__(self):
        return f"{self.term}\n{self.content[1]}"

    @property
    def active(self):
        """Return if this arg is active."""
        if not self.is_arg:
            return True

        # otherwise, simply check for any alphanumeric characters in the
        # term. Normally these terms are just '--' or '--,--'
        return self.term.any_isalnum

    @property
    def is_arg(self):
        """Return True when this variable list is for an argument."""
        anc = list(self._element.iterancestors())
        if not anc:
            return False
        val = anc[0].tag == "variablelist" and anc[1].tag == "refsynopsisdiv"
        if not val:
            # miscoded?
            elem_id = anc[1].get("id")
            if elem_id:
                val = "argdescript" in elem_id
        return val

    def py_text(self, links=None, base_url=None, fcache=None):
        """Remove mention of graphical interaction."""
        if self.text.tag in item_needing_all:
            rst = self.text.to_rst(links=links, base_url=base_url, fcache=fcache)
        elif self.text.tag in item_needing_links_base_url:
            rst = self.text.to_rst(links=links, base_url=base_url)
        elif self.text.tag in item_needing_fcache:
            rst = self.text.to_rst(links=links, fcache=fcache)
        else:
            rst = self.text.to_rst()
        if "graphical" in rst:
            valid = []
            for sentence in rst.split(". "):
                if "GUI" not in sentence:
                    valid.append(sentence)
            rst = ". ".join(valid)
        return rst

    def to_rst(self, prefix="", links=None, base_url=None, fcache=None):
        prefix += "    "
        # if this is a parameter arg
        if self.is_arg:
            lines = [f"{self.py_term(links=links, base_url=base_url)}"]
            lines.append(
                textwrap.indent(
                    self.py_text(links=links, base_url=base_url, fcache=fcache),
                    prefix,
                )
            )
            return "\n".join(lines)

        # term_text = [line.strip() for line in self.py_text.splitlines()]
        # term_text = term_text[0] + '\n' + textwrap.indent('\n'.join(term_text[1:]), )

        lines = [
            f"* ``{self.py_term(links=links, base_url=base_url)}`` - {textwrap.indent(self.py_text(links=links, base_url=base_url, fcache=fcache), prefix)}"  # noqa : E501
        ]
        text = "\n".join(lines)
        # if 'ID number to which this tip belongs' in text:
        # breakpoint()
        return text


class Term(Element):
    """Term element."""

    def to_rst(self, prefix="", links=None, base_url=None, fcache=None):

        items = []
        for item in self:
            if isinstance(item, Element):
                if item.tag in item_needing_links_base_url:
                    items.append(item.to_rst(links=links, base_url=base_url))
                elif item.tag in item_needing_fcache:
                    items.append(item.to_rst(fcache=fcache))
                else:
                    items.append(item.to_rst())
            else:
                items.append(str(item))

        text = ", ".join(items)
        if text.endswith("–"):
            text = text[:-1]
        return text

    def __repr__(self):
        out = super().__repr__()
        return ", ".join(out.split(","))


class GuiLabel(Element):
    """GuiLabel element."""

    pass


class GuiMenuItem(Element):
    """GuiMenuItem element."""

    pass


class SuperScript(Element):
    """Superscript element."""

    def to_rst(self, prefix=""):
        return f":sup:`{self.content[0]}` {self.tail}"


class Code(Element):
    """Code element."""

    pass


class _Math(Element):
    def __init__(self, element):
        self._element = element
        self._content = []
        self._parse_equation(element)

    def _parse_equation(self, eqn):
        raw = tostring(eqn).decode().replace("xmlns:m", "xmlns")
        raw = raw.replace('display="block"', "")
        raw = raw.replace("<mtext>&#8202;</mtext>\n", "")
        raw = raw.replace("<mtext>&#8201;</mtext>\n", "")
        try:
            parsed = MathML2Tex().translate(raw, network=False, from_file=False)
            parsed = parsed.replace("\\hspace", "").strip()
            self._content = [parsed]
        except NameError:
            self._content = [""]

    def __repr__(self):
        try:
            return LatexNodes2Text().latex_to_text(self.equation)
        except NameError:
            return "<Equation>"

    @property
    def equation(self):
        return self.content[0][1:-1]


class Math(_Math):
    """Math element."""

    def to_rst(self, prefix=""):
        lines = ["", "", f"{prefix}.. math::\n"]
        lines.append(textwrap.indent(self.equation, prefix=prefix + " " * 4))
        lines.append("")
        return "\n".join(lines)


class InlineEquation(_Math):
    """Inline equation element."""

    def __init__(self, element):
        self._element = element
        self._content = []
        self._parse_equation(element.find("math"))

    @property
    def tail(self):
        return self.raw.split("</inlineequation>")[-1].replace("\n", "")

    def to_rst(self, prefix=""):
        return f":math:`{self.equation.strip()}` {self.tail}"


class SubScript(Element):
    """Inline equation element."""

    def __init__(self, element):
        super().__init__(element)


class InlineGraphic(Element):
    """Inline graphic element."""

    def fileref(self):
        """File reference."""
        return self._element.get("fileref")


class Quote(Element):
    """Quote element."""

    def __init__(self, element):
        super().__init__(element)
        # self._content[0] = f"{self._content[0]}"

    @property
    def quote(self):
        return self[0]

    def __repr__(self):
        return f'"{self.quote}" {self.tail}'


class Link(Element):
    """Link element."""

    def __init__(self, element):
        super().__init__(element)
        self._linkend = element.get("linkend")

    @property
    def linkend(self):
        """Return Link."""
        return self._linkend

    def __repr__(self):
        return str(self.linkend)

    def to_rst(self, prefix="", links=None, base_url=None):
        if (links or base_url) is None:
            print("ERROR in the links or the base_url definitions - Link class.")
        tail = " ".join([str(item) for item in self])
        tail = self.tail.replace("\n", "")
        if self.linkend in links:
            root_name, root_title, href, text = links[self._linkend]
            root_title = root_title.replace("\n", "")
            link = f"{base_url}{root_name}/{href}"
            return f"`{root_title} <{link}>`_ {tail}"

        # missing link...
        return tail


class XRef(Link):
    """XRef element."""

    @property
    def tail(self):
        return " ".join([str(item) for item in self._content])

    def to_rst(self, prefix=""):
        # disabled at the moment
        # return f':ref:`{self.linkend}`{self.tail}'
        return self.tail


class UserInput(Element):
    """UserInput."""

    pass


class Screen(Element):
    """Screen output (effectively literal output)."""

    pass


class Literal(Element):
    """Screen output (effectively literal output)."""

    def to_rst(self, prefix=""):
        return f"``{self.content[0]}`` {self.tail}"


class Caution(Element):
    """Screen output (effectively literal output)."""

    def to_rst(self, prefix=""):
        lines = ["", "", ".. warning::"]
        lines.append(textwrap.indent(str(self), prefix=prefix + "   "))
        return "\n".join(lines)


class Graphic(Element):
    """Graphic element."""

    @property
    def entityref(self):
        entityref = self.get("entityref")
        if entityref is not None:
            entityref = entityref.strip()
        return entityref

    def to_rst(self, fcache, prefix=""):

        if self.entityref is None:
            # probably a math graphics
            fileref = self.get("fileref")
            if fileref is not None and "mathgraphics" in fileref:
                return ""

        if self.entityref == "Linebrk":
            return f"\n\n"

        if self.entityref in fcache:
            filename = fcache[self.entityref]
            text = f"\n\n{prefix}.. figure:: ../images/{filename}\n"
            return text

        return ""


class Function(Element):
    """Function element."""

    pass


class Note(Element):
    """Note element."""

    pass


class BlockQuote(Element):
    """Note element."""

    def to_rst(self, prefix="", links=None, base_url=None, fcache=None):
        items = []
        for item in self:
            if isinstance(item, Element):
                if item.tag in item_needing_all:
                    items.append(
                        item.to_rst(
                            prefix,
                            links=links,
                            base_url=base_url,
                            fcache=fcache,
                        )
                    )
                elif item.tag in item_needing_links_base_url:
                    items.append(item.to_rst(prefix, links=links, base_url=base_url))
                elif item.tag in item_needing_fcache:
                    items.append(item.to_rst(prefix=prefix, fcache=fcache))
                else:
                    items.append(item.to_rst(prefix))
            else:
                items.append(prefix + str(item))
        return "\n\n" + " ".join(items) + "\n\n"


class RefMeta(Element):
    """Reference metadata element."""

    @property
    def refentry_title(self):
        title = self.rec_find("Refentrytitle")
        if title is not None:
            return str(title).strip()
        return ""


class IndexTerm(Element):

    pass


class Primary(Element):

    pass


unsup_elem = set()


def parse_element(element):
    """Parse a single element."""
    if element.tag not in parsers:
        if "cython_function" in str(type(element.tag)):
            return Element(element)

        # warnings.warn(f"Unsupported element tag '{element.tag}'")
        return Element(element)

    return parsers[element.tag](element)


def parse_children(element):
    """Parse an element."""

    children = []
    for child in element.getchildren():
        if child.tag in parsers:
            children.append(parsers[child.tag](child))
        else:
            children.append(child)
    return children


def parse_text(element):
    """Parse a paragraph element."""
    if element is not None:
        return " ".join(element.text_content().split())
    return ""


class TGroup(Element):
    @property
    def n_col(self):
        return self._element.get("cols")

    @property
    def thead(self):
        """THead."""
        return self.find("THead")

    @property
    def tbody(self):
        """TBody."""
        return self.find("TBody")

    @property
    def row_in_tbody(self):
        """List of the rows in TBody."""
        return self.find("TBody").find_all("Row")

    def to_rst(self, prefix="", links=None, base_url=None):

        l_head = 0

        if self.thead is not None:
            rows, l_head = self.thead.to_rst(links=links, base_url=base_url)
        else:
            rows = [".. flat-table::"]
            rows.append("")

        if self.row_in_tbody is not None:

            rst_tbody = self.tbody.to_rst(l_head, links=links, base_url=base_url)
            if len(rst_tbody) > 0:
                rows += rst_tbody

        return "\n".join(rows)


class Table(Element):
    @property
    def title(self):
        """Table title."""
        return self.find("Title")

    @property
    def tgroup(self):
        """TGroup."""
        return self.find("TGroup")

    def to_rst(self, prefix="", links=None, base_url=None):
        if SUPPORT_TABLES:
            lines = []
            if self.title is not None:
                lines.append(f"{self.title}".strip())
                lines.append((len(lines[-1]) * "="))
                lines.append("")

            if self.tgroup is not None:
                a = self.tgroup
                lines.append(a.to_rst(links=links, base_url=base_url))

            return "\n".join(lines)

        else:
            return "\nTable redacted."

    def __repr__(self):
        return self.to_rst()


class Refentrytitle(Element):
    """Title."""

    def __repr__(self):
        items = []
        for item in self._content:
            item = str(item)
            for key, value in CONST.items():
                item = item.replace(key, value)
            items.append(item)
        return "".join(items)


class Refnamediv(Element):
    def __init__(self, element, terms_global=None):
        self._element = element
        self._terms_global = terms_global
        super().__init__(element)

    @property
    def terms_global(self):
        return self._terms_global

    @terms_global.setter
    def terms_global(self, terms_global):
        self._terms_global = terms_global

    @property
    def refname(self):
        return self.find("Refname", self._terms_global)

    @property
    def purpose(self):
        return self.find("Refpurpose")


class Refname(Element):
    def __init__(self, element, terms_global=None):
        self._element = element
        self._terms_global = terms_global
        super().__init__(element)

    @property
    def terms_global(self):
        return self._terms_global

    @terms_global.setter
    def terms_global(self, terms_global):
        self._terms_global = terms_global

    @property
    def raw_args(self):
        mapdl_cmd = str(self)
        mapdl_cmd = mapdl_cmd.replace("&fname_arg;", self._terms_global["fname_arg"])
        mapdl_cmd = mapdl_cmd.replace("&fname1_arg;", self._terms_global["fname1_arg"])
        mapdl_cmd = mapdl_cmd.replace("&fname2_arg;", self._terms_global["fname2_arg"])
        mapdl_cmd = mapdl_cmd.replace("&pn006p;", self._terms_global["pn006p"])
        mapdl_cmd = mapdl_cmd.replace("&ansysBrand;", self._terms_global["ansysBrand"])
        split_args = mapdl_cmd.split(",")[1:]
        return split_args

    @property
    def args(self):
        args = []
        for item in self.raw_args:
            orig_arg = str(item).replace(",", "")
            arg = orig_arg.lower().replace("--", "").replace("–", "").replace("-", "_").strip()
            if arg == "":
                continue

            if arg == "class":
                arg = "class_"
            elif arg == "type":
                arg = "type_"

            # simply check if we can use this as a valid python kwarg
            try:
                exec(f"{arg} = 1.0")
            except SyntaxError:
                continue

            if "blank" in arg:
                continue

            args.append(arg)

        # rename duplicate arguments
        if len(args) != len(set(args)):
            for arg in args:
                i = 0
                if args.count(arg) > 1:
                    for j in range(len(args)):
                        if args[j] == arg:
                            args[j] = f"{arg}{i:d}"
                            i += 1

        return args


class Refpurpose(Element):
    def __repr__(self):
        return " ".join([str(item) for item in self._content])


class Refclass(Element):

    pass


class Application(Element):

    pass


class Refsect1(Element):

    pass


class Command(Element):
    """Command element."""

    @property
    def command(self):
        return self[0]

    @property
    def tail_no_args(self):
        tail = self.tail
        for arg in self.args:
            tail = tail.replace(arg, "")
        return tail

    def __repr__(self):
        return f"{self.command} {self.tail}"

    @property
    def has_args(self):
        # return self.tail.startswith(",")
        return False

    @property
    def args(self):
        """Any terms immediately following the command."""
        if self.has_args:
            words = self.tail.split()
            cmd_args = words[0]

            # Remove trailing non-alphanumeric. These can't be part of the command.
            while cmd_args and not (cmd_args[-1].isalnum() or cmd_args[-1].isdigit()):
                cmd_args = cmd_args[:-1]

            # possible that next element is a replaceable and not part of the tail
            if isinstance(self.next_elem, Replaceable):
                cmd_args += str(self.next_elem[0])  # no tail
            elif len(self.tail) > 1 and self.tail[1] == " ":
                # possible not coded as replacable
                for word in words[1:]:
                    if word.upper() == word or is_numeric(word):
                        if not (word[-1].isalnum() or word[-1].isdigit()):
                            parm, _ = split_trail_alpha(word)
                        else:
                            parm = word

                        if parm:
                            cmd_args += f",{parm}"
                    else:
                        # break at first failing match
                        break

            return cmd_args.split(",")[1:]
        return [""]

    @property
    def py_args(self):
        args = []
        for arg in self.args:
            if is_numeric(arg):
                args.append(f"{arg}")
            else:
                args.append(f'"{arg}"')
        py_args = ", ".join(args)
        if py_args == '""':
            return ""
        return py_args

    @property
    def py_cmd(self):
        return to_py_name(self.command)

    @property
    def sphinx_cmd(self):
        if self.has_args:
            py_args = self.py_args
        else:
            py_args = ""

        return f":ref:`{self.py_cmd}`"

    def to_rst(self, prefix=""):
        """Convert to an rst format."""
        if self.args and self.args[0] != "":
            return f"{self.sphinx_cmd} {self.tail_no_args}"
        else:
            return f"{self.sphinx_cmd} {self.tail}"


class ComputerOutput(Element):
    def to_rst(self, prefix=""):
        return f"``{self[0]}`` {self[1]}"


class Figure(Element):
    """Figure element."""

    @property
    def title(self):
        return self.rec_find("Title")

    @property
    def graphic(self):
        return self.rec_find("Graphic")

    def to_rst(self, prefix="", fcache=None):
        graphic = self.graphic
        if graphic is not None and graphic.entityref is not None:
            lines = []
            lines.append(graphic.to_rst(prefix=prefix, fcache=fcache))
            if self.title is not None:
                lines.append(f"   {self.title}")

            return "\n" + "\n".join(lines) + "\n"

        items = []
        for item in self:
            if isinstance(item, Element):
                if item.tag in item_needing_fcache:
                    items.append(item.to_rst(prefix=prefix, fcache=fcache))
                else:
                    items.append(item.to_rst(prefix))
            else:
                items.append(prefix + str(item))
        return "\n" + "".join(items)


class Footnote(Element):

    pass


class Footnoteref(Element):

    pass


class Formalpara(Element):

    pass


class Glossterm(Element):

    pass


class Guibutton(Element):

    pass


class Guiicon(Element):

    pass


class Highlights(Element):

    pass


class Important(Element):

    pass


class Informalequation(Element):

    pass


class Interface(Element):

    pass


class Markup(Element):

    pass


class Mediaobject(Element):

    pass


class Option(Element):

    pass


class Refsect3(Element):

    pass


class Refsynopsisdiv(Element):

    pass


class Sidebar(Element):

    pass


class XMLType(Element):

    pass


class XMLWarning(Element):

    pass


class ClassName(Element):

    pass


class Imageobject(Element):

    pass


class Informalfigure(Element):

    pass


class Envar(Element):

    pass


class ImageData(Element):

    pass


class ColSpec(Element):

    pass


class TBody(Element):
    @property
    def rows(self):
        return self.find_all("Row")

    def to_rst(self, l_head, prefix="", links=None, base_url=None):
        rst_rows = []
        for i, row_i in enumerate(self.rows):
            row = row_i.find_all("Entry")
            if len(row[0]) > 0:
                if type(row[0][0]) == Command:
                    command = f"   * - :ref:`{row[0][0].py_cmd}`"
                    rst_rows.append(command)
                    strg = f"     - {row[1][0]}"
                    rst_rows.append(strg)
                    if l_head == 0 and i == 0:
                        l_head = 2
                else:
                    if l_head == 0 and i == 0:
                        row_rst_list = row_i.to_rst_list(links=links, base_url=base_url)
                        l_head = len(row_rst_list)

                    else:
                        row_rst_list = row_i.to_rst_list(links=links, base_url=base_url)
                    row_rst = "\n     - ".join(row_rst_list)
                    rst_rows.append(f"   * - {row_rst}")
            elif len(row[1]) > 0:
                if type(row[1][0]) == Command:
                    command = f"   * - :ref:`{row[1][0].py_cmd}`"
                    rst_rows.append(command)
                    strg = "     - " + str(row[2][0])
                    rst_rows.append(strg)

        return rst_rows


class Entry(Element):
    @property
    def morerows(self):
        return self._element.get("morerows")

    def to_rst(self, prefix="", links=None, base_url=None, fcache=None):

        if self.morerows is not None:
            content = self.morerows

        items = []
        for item in self:
            if isinstance(item, Element):
                if item.tag in item_needing_links_base_url:
                    items.append(item.to_rst(prefix, links=links, base_url=base_url))
                else:
                    items.append(item.to_rst(prefix))
            else:
                items.append(str(item))

        if self.morerows is not None:
            entry = f":rspan:`{content}` " + " ".join(items)

        else:
            entry = " ".join(items)

        return entry


class Row(Element):
    @property
    def entry(self):
        return self.find_all("Entry")

    def to_rst_list(self, prefix="", links=None, base_url=None):
        row = []
        for entry in self.entry:
            content = entry.to_rst(links=links, base_url=base_url)
            content = content.replace("\n", "")
            content = content.replace("\r", "")
            row.append(content)
        return row


class THead(Element):
    @property
    def rows(self):
        return self.find_all("Row")

    def to_rst(self, prefix="", links=None, base_url=None):

        l_rst_list = 0

        if self.rows is not None:
            row = []

            if len(self.rows) > 1:
                row.append(
                    f".. flat-table:: {''.join(self.rows[0].to_rst_list(links=links, base_url=base_url))}"  # noqa : E501
                )
                row.append(f"   :header-rows: {len(self.rows)-1}")
                ini = 1

            elif len(self.rows[0]) == 1:
                row.append(self.rows[0].to_rst_list(links=links, base_url=base_url)[0])
                row.append("")
                row.append(f".. flat-table::")
                ini = len(self.rows)

            else:
                row.append(f".. flat-table::")
                row.append(f"   :header-rows: 1")
                ini = 0

            row.append("")

            for i in range(ini, len(self.rows)):
                rst_list = self.rows[i].to_rst_list(links=links, base_url=base_url)
                l_rst_list = len(rst_list)
                row_rst = "\n     - ".join(rst_list)
                row.append(f"   * - {row_rst}")

            return row, l_rst_list


class Remark(Element):

    pass


class LiteralLayout(Element):

    pass


class CiteTitle(Element):

    pass


class ULink(Element):

    pass


class SegTitle(Element):

    pass


class Chapter(Element):
    @property
    def helpstring(self):
        return self[1]._element.get("helpstring")

    def __repr__(self):
        items = [f"Chapter {self.helpstring}\n\n"]
        items.extend([str(item) for item in self._content])
        return "".join(items)


class Section1(Element):

    pass


class ProductName(Element):

    pass


class MAPDLCommand(Element):
    """MAPDL command from documentation."""

    def __init__(
        self,
        filename,
        terms_global,
        docu_global,
        PYMAPDL_CLASS,
        links,
        base_url,
        fcache,
        meta_only=False,
    ):
        """Parse command from xml file."""
        self._xml_filename = filename
        self._terms_global = terms_global
        self._docu_global = docu_global
        self._PYMAPDL_CLASS = PYMAPDL_CLASS
        self._links = links
        self._base_url = base_url
        self._fcache = fcache
        root = fromstring(open(filename, "rb").read())

        # ensure that refentry exists
        try:
            self._refentry = next(root.iterfind(".//refentry"))
        except StopIteration:
            raise RuntimeError("Not a command file")

        # parse the command
        super().__init__(self._refentry, parse_children=not meta_only)

    @property
    def xml_filename(self):
        """Return the source filename of the command."""
        return self._xml_filename

    @property
    def args(self):
        """Return the command args."""
        return self._refname_div.refname.args

    @property
    def default(self):
        if self._refsynopsis:
            for item in self._refsynopsis:
                if str(item.title).strip() == "Command Default":
                    return item

    @property
    def arg_desc(self):
        """Return each argument's description."""
        refsyn = self.rec_find("Refsynopsisdiv")

        # search by ID
        if refsyn is None:
            for elem in self.find_all("RefSection"):
                if elem.id is not None and "argdescript" in elem.id:
                    return elem

        return refsyn

    @property
    def short_desc(self):
        """Return the short description of the command."""
        if self._refname_div is not None:
            return self._refname_div.purpose.to_rst(links=self._links, base_url=self._base_url)
        return ""

    @property
    def _metadata(self):
        if self.rec_find("RefMeta") is None:
            for item in self._refentry.getchildren():
                if item.tag == "refmeta":
                    return parse_element(item)
        return self.rec_find("RefMeta")

    @property
    def name(self):
        return self._metadata.refentry_title

    @property
    def py_name(self):
        """Python compatible name."""
        return to_py_name(self.name)

    @property
    def py_args(self):
        return [arg.lower() for arg in self.args]

    @property
    def py_signature(self):
        args = ["self"]
        kwargs = [f'{arg}=""' for arg in self.py_args if "--" not in arg]
        arg_sig = ", ".join(args + kwargs)
        return f"def {self.py_name}({arg_sig}):"

    @property
    def py_docstring(self):
        """Return the python docstring of this MAPDL command."""
        apdl_cmd = f"{self._terms_global['pn006p']} Command: `{self.name} <{self.url}>`_"

        items = [self.short_desc, "", apdl_cmd]

        if self.default is not None:
            if self.default.tag in item_needing_links_base_url:
                items += [""] + textwrap.wrap(
                    "Default: " + self.default.to_rst(links=self._links, base_url=self._base_url)
                )
            else:
                items += [""] + textwrap.wrap("Default: " + self.default.to_rst())
        if self.args is not None:
            items += [""] + self.py_parm
        if self.notes is not None:
            items += [""] + self.py_notes
        docstr = "\n".join(items)

        # final post-processing
        def replacer(match):
            return match.group().replace("*", r"\*")

        # sphinx doesn't like asterisk symbols
        docstr = re.sub(r"(?<=\S)\*|(\*\S)", replacer, docstr)

        for key, value in CONST.items():
            docstr = docstr.replace(key, value)
        for key, value in CLEANUP.items():
            docstr = docstr.replace(key, value)

        # delete trailing whitespace for each line
        docstr = "\n".join(line.rstrip() for line in docstr.splitlines())

        # sub MAPDL command args
        def arg_replacer(match):
            text = match.group().replace("`", "")
            func = re.findall(r"<CMD>(.*)</CMD>", text)[0]
            arg_str = text.split("</CMD>")[1].strip()[1:]
            if arg_str.endswith(","):
                arg_str = arg_str[:-1]
            if arg_str.startswith(","):
                arg_str = arg_str[1:]

            split_args = [arg.strip() for arg in arg_str.split(",")]

            tail = ""
            py_args = []
            if split_args[-1] == "or":
                # these are options and not args. Use the first and ignore the rest
                tail = text.split(split_args[0])[-1]
                split_args = [split_args[0]]

                for arg in split_args:
                    if is_numeric(arg):
                        py_args.append(f"{arg}")
                    else:
                        py_args.append(f'"{arg}"')
            py_args = ", ".join(py_args)

            return f":func:`{func}({py_args}) <{self._PYMAPDL_CLASS}.{func}>` {tail}"

        # command replacement with args
        docstr = re.sub(
            r"<CMD>[a-z0-9]*</CMD>?(\s*,+\s*[A-Za-z0-9%`]*)+",
            arg_replacer,
            docstr,
        )

        def cmd_replacer(match):
            func = match.group().replace("<CMD>", "").replace("</CMD>", "")
            return f":func:`{func}() <{self._PYMAPDL_CLASS}.{func}>`"

        # command replacement without args
        docstr = re.sub(r"<CMD>[a-z0-9]*</CMD>", cmd_replacer, docstr)

        def pipe_replacer(match):
            return match.group().replace("|", "\|")

        docstr = re.sub(r"\|(.*)\|", pipe_replacer, docstr)

        def trail_replacer(match):
            return match.group().replace("_", "")

        docstr = re.sub(r"([^_|^`][A-Za-z0-9]*)_\s", trail_replacer, docstr)

        def term_replacer(match):
            term = match.group()[1:-1]
            if term in self._docu_global:
                _, key, cite_title = self._docu_global[term]
                if key in self._links:
                    root_name, root_title, href, text = self._links[key]
                    link = f"{self._base_url}{root_name}/{href}"
                    link_text = self._terms_global.get(cite_title, root_title)
                    return f"`{link_text} <{link}>`_"
            else:
                if term not in self._terms_global:
                    warnings.warn(f"term {term} not in terms_global")
                    return ""
                return self._terms_global[term]

        docstr = re.sub(r"&[\S]*?;", term_replacer, docstr)

        # final line by line cleanup
        lines = []
        for line in docstr.splitlines():
            if "cannot be accessed from a menu" in line:
                continue
            if "Graphical picking is available only" in line:
                continue
            lines.append(line)

        # ensure the hierarchy of the titles
        is_equal_sign = False
        is_dash_sign = False
        i = 0
        while i < len(lines):
            if lines[i].lstrip().startswith("-"):
                if is_dash_sign == False:
                    is_dash_sign = True
            elif lines[i].lstrip().startswith("="):
                if is_equal_sign or is_dash_sign:
                    lines[i - 1] = "**" + lines[i - 1] + "**"
                    # print("après : ", lines[i-1])
                    lines.pop(i)
                if is_equal_sign == False:
                    is_equal_sign = True

            i += 1

        # ensure that lists begin with list-table
        i = 2
        while i < len(lines):
            header = lines[i - 2].lstrip().startswith(":header-rows:") or lines[
                i - 2
            ].lstrip().startswith(".. flat-table")
            corp = lines[i - 1].lstrip().startswith("* -") or lines[i - 1].lstrip().startswith("-")
            if (lines[i].lstrip().startswith("* -")) and not (corp or header):
                lines.insert(i, ".. flat-table ::")
                lines.insert(i + 1, "")
            i += 1

        # ensure that lists end with a blank line
        i = 0
        while i < len(lines):
            j = 1
            if lines[i].lstrip().startswith("* -"):
                while i + j < len(lines) - 1 and lines[i + j].lstrip().startswith("-"):
                    j += 1
                if not lines[i + j].lstrip().startswith("* -"):
                    if i + j == len(lines) - 1:
                        j += 1
                    lines.insert(i + j, "")
            i += j

        # ensure that two similar links are not in a similar file.
        i = 0
        link = []
        flat_table = False
        while i < len(lines):
            n_quotes = lines[i].count("`")
            if ".. flat-table::" in lines[i]:
                flat_table = True
            if flat_table is True:
                if n_quotes > 0:
                    j = 0
                    quote = 0
                    begin = False
                    while quote < n_quotes and j < len(lines[i]):
                        if lines[i][j] == "`":
                            if begin == False:
                                begin = True
                                link_i = []
                                quote += 1
                            else:
                                link.append(link_i)
                                begin = False
                                quote += 1
                        else:
                            if begin == True:
                                link_i.append(lines[i][j])
                        j += 1
            i += 1

        link_list = []
        for l in link:
            if "<" in "".join(l):
                link_list.append("".join(l))

        if len(link_list) > 1:
            diff_links = set(link_list)
            if len(diff_links) != len(link_list):
                for l in diff_links:
                    name_link = l[: l.index("<") - 1]
                    nb_l = link_list.count(l)
                    if nb_l > 1:
                        first = 0
                        flat_table = False
                        for i in range(len(lines)):
                            if ".. flat-table::" in lines[i]:
                                flat_table = True
                            if flat_table is True:
                                if lines[i].count(l) > 0:
                                    if first == 0:
                                        first = 1
                                    else:
                                        print("REPLACE", lines[i])
                                        lines[i] = lines[i].replace(l, name_link)

        docstr = "\n".join(lines)

        # remove repeated line breaks
        while "\n\n\n" in docstr:
            docstr = docstr.replace("\n\n\n", "\n\n")

        docstr = re.sub(r"bgcolor=\S\S\S\S\S\S\S\S\S\S?", "", docstr)
        docstr = re.sub(r"_cellfont Shading=\S\S\S\S\S\S\S\S", "", docstr)

        return docstr

    @property
    def py_notes(self):
        """Return the python formatted notes string."""
        lines = ["Notes", "-" * 5]
        if self.notes.tag in item_needing_all:
            lines.append(
                self.notes.to_rst(
                    links=self._links,
                    base_url=self._base_url,
                    fcache=self._fcache,
                )
            )
        elif self.notes.tag in item_needing_links_base_url:
            lines.append(self.notes.to_rst(links=self._links, base_url=self._base_url))
        elif self.notes.tag in item_needing_fcache:
            lines.append(self.notes.to_rst(links=self._links, fcache=self._fcache))
        else:
            lines.append(self.notes.to_rst())

        return lines

    @property
    def py_parm(self):
        """Return the python parameters string."""
        if self.arg_desc is not None:
            lines = ["Parameters", "-" * 10]
            for item in self.arg_desc:
                if not isinstance(item, Variablelist):
                    if isinstance(item, Element) and "Command Default" in str(item.title):
                        continue
                if isinstance(item, Element):
                    if item.tag in item_needing_all:
                        lines.append(
                            item.to_rst(
                                links=self._links,
                                base_url=self._base_url,
                                fcache=self._fcache,
                            )
                        )
                    elif item.tag in item_needing_links_base_url:
                        lines.append(item.to_rst(links=self._links, base_url=self._base_url))
                    elif item.tag in item_needing_fcache:
                        lines.append(item.to_rst(fcache=self._fcache))
                    else:
                        lines.append(item.to_rst())
                else:
                    lines.append(str(item))
            return lines
        return []

    @property
    def url(self):
        """Return the URL to the Ansys command documentation."""
        cmd_base_url = f"{self._base_url}/ans_cmd/"
        return f"{cmd_base_url}{self.filename}"

    @property
    def filename(self):
        """Command filename"""
        return self[0]._element.get("filename")

    @property
    def _refname_div(self):
        return self.rec_find("Refnamediv", self._terms_global)

    @property
    def _refsynopsis(self):
        return self.find("Refsynopsisdiv")

    @property
    def notes(self):
        for item in self:
            if str(item.title).strip() == "Notes":
                return item

    def __repr__(self):
        lines = [f"APDL Command: {self.name}"]
        lines.append("")
        lines.append("Short Description:")
        lines.append(f"{self.short_desc}")
        lines.append("")
        lines.append("Function signature:")
        lines.append(", ".join([f"{self.name}"] + self.args))
        lines.append("")
        lines.append(str(self.arg_desc))
        lines.append("")
        lines.append(str(self.notes))

        return "\n".join(lines)

    @property
    def py_source(self):
        """Return the python source"""
        return textwrap.indent("pass\n", prefix=" " * 4)

    def to_python(self, prefix=""):
        docstr = textwrap.indent(f'\nr"""{self.py_docstring}\n"""', prefix=prefix + " " * 4)
        return f"{self.py_signature}{docstr}\n{self.py_source}"


class InformalTable(Element):
    def to_rst(self, prefix=""):
        return "InformalTables need to be added"


parsers = {
    "sect1": Section1,
    "chapter": Chapter,
    "productname": ProductName,
    "ulink": ULink,
    "segtitle": SegTitle,
    "citetitle": CiteTitle,
    "literallayout": LiteralLayout,
    "remark": Remark,
    "tbody": TBody,
    "entry": Entry,
    "row": Row,
    "thead": THead,
    "colspec": ColSpec,
    "tgroup": TGroup,
    "envar": Envar,
    "term": Term,
    "varlistentry": VarlistEntry,
    "imagedata": ImageData,
    "imageobject": Imageobject,
    "informalfigure": Informalfigure,
    "classname": ClassName,
    "classname": ClassName,
    "computeroutput": ComputerOutput,
    "figure": Figure,
    "footnote": Footnote,
    "footnoteref": Footnoteref,
    "formalpara": Formalpara,
    "glossterm": Glossterm,
    "guibutton": Guibutton,
    "guiicon": Guiicon,
    "highlights": Highlights,
    "important": Important,
    "informalequation": Informalequation,
    "interface": Interface,
    "markup": Markup,
    "mediaobject": Mediaobject,
    "option": Option,
    "refsect3": RefSection,
    "refsynopsisdiv": Refsynopsisdiv,
    "sidebar": Sidebar,
    "type": XMLType,
    "warning": XMLWarning,
    "refsect1": RefSection,
    "application": Application,
    "refclass": Refclass,
    "refpurpose": Refpurpose,
    "refname": Refname,
    "refnamediv": Refnamediv,
    "refentrytitle": Refentrytitle,
    "primary": Primary,
    "indexterm": IndexTerm,
    "refmeta": RefMeta,
    "function": Function,
    "refsect2": RefSection,
    "informalexample": InformalExample,
    "graphic": Graphic,
    "caution": Caution,
    "literal": Literal,
    "userinput": UserInput,
    "screen": Screen,
    "xref": XRef,
    "subscript": SubScript,
    "inlinegraphic": InlineGraphic,
    "math": Math,
    "inlineequation": InlineEquation,
    "member": Member,
    "simplelist": SimpleList,
    "link": Link,
    "quote": Quote,
    "guimenuitem": GuiMenuItem,
    "itemizedlist": ItemizedList,
    "listitem": ListItem,
    "olink": OLink,
    "replaceable": Replaceable,
    "emphasis": Emphasis,
    "example": Example,
    "command": Command,
    "title": Title,
    "para": Paragraph,
    "table": Table,
    "orderedlist": OrderedList,
    "variablelist": Variablelist,
    "bridgehead": parse_text,
    "informaltable": InformalTable,
    "blockquote": BlockQuote,
    "note": Note,
    "programlisting": ProgramListing,
    "guimenu": GuiMenu,
    "phrase": Phrase,
    "structname": Structname,
    "filename": FileName,
    "superscript": SuperScript,
    "guilabel": GuiLabel,
    "code": Code,
}

item_needing_links_base_url = {
    "table": Table,
    "simplelist": SimpleList,
    "variablelist": Variablelist,
    "varlistentry": VarlistEntry,
    "refsect2": RefSection,
    "refsect3": RefSection,
    "link": Link,
    "itemizedlist": ItemizedList,
    "olink": OLink,
    "phrase": Phrase,
    "listitem": ListItem,
    "emphasis": Emphasis,
    "formalpara": Formalpara,
    "orderedlist": OrderedList,
    "note": Note,
    "sidebar": Sidebar,
    "title": Title,
    "blockquote": BlockQuote,
    "term": Term,
    "para": Paragraph,
    "refsect1": RefSection,
    "member": Member,
    "highlights": Highlights,
    "important": Important,
    "footnote": Footnote,
}

item_needing_fcache = {
    "graphic": Graphic,
    "figure": Figure,
    "term": Term,
    "para": Paragraph,
    "refsect1": RefSection,
    "refsect2": RefSection,
    "refsect3": RefSection,
    "simplelist": SimpleList,
    "itemizedlist": ItemizedList,
    "listitem": ListItem,
    "informalfigure": Informalfigure,
    "variablelist": Variablelist,
    "blockquote": BlockQuote,
    "informalequation": Informalequation,
}

item_needing_all = {
    "itemizedlist": ItemizedList,
    "variablelist": Variablelist,
    "simplelist": SimpleList,
    "term": Term,
    "para": Paragraph,
    "refsect1": RefSection,
    "refsect2": RefSection,
    "refsect3": RefSection,
    "listitem": ListItem,
    "varlistentry": VarlistEntry,
    "blockquote": BlockQuote,
}


def get_parser():
    return parsers


class OxygenXmlTree(Element):
    """Load an XML file represented as an AST."""

    def __init__(self, filename, meta_only=False):
        """Parse command from xml file."""
        self._xml_filename = filename
        root = fromstring(open(filename, "rb").read())

        # parse the file
        super().__init__(root, parse_children=not meta_only)

    @property
    def xml_filename(self):
        """Return the source filename of the command."""
        return self._xml_filename


# # ############################################################################
# # # Ansys Documentation path
# # ############################################################################

# # TODO: generalize the implementation to become an open-source library


# def create_doc_path(doc_path=None):
#     # Declaration
#     if doc_path is None:

#         parser = argparse.ArgumentParser()
#         parser.add_argument("--xml-doc-path", help="XML Documentation path")

#         args = parser.parse_args()

#         doc_path = args.xml_doc_path
#         if doc_path is None:
#             doc_path = os.environ.get("XML_DOC_PATH")
#         if doc_path is None:
#             raise RuntimeError(
#                 "Missing the XML documentation path. Specify this with either --xml-doc-path or set the XML_DOC_PATH environment variable" # noqa : E501
#             )

#         doc_path = os.path.abspath(os.path.expanduser(doc_path))

#     # Verification
#     if not os.path.isdir(doc_path):
#         raise FileNotFoundError(f"Documentation path at {doc_path} does not exist")

#     return doc_path


# def create_glb_cmd_path(doc_path):
#     glb_path = os.path.join(doc_path, "global")
#     cmd_path = os.path.join(doc_path, "docu_files/ans_cmd")
#     if not os.path.isdir(cmd_path):
#         raise FileNotFoundError(
#             f'Invalid documentation path. "docu_files" does not appear to '
#             "be a directory within the documentation path at:"
#             f"{doc_path}"
#         )
#     return glb_path, cmd_path


# def load_links(glb_path):
#     """Load all links."""

#     linkmaps = os.path.join(glb_path, "linkmaps", "db", "*.db")
#     linkmap_fnames = list(glob.glob(linkmaps, recursive=True))
#     links = {}

#     for filename in tqdm(linkmap_fnames, desc="Loading links"):
#         try:
#             linkmap = Element(fromstring(open(filename, "rb").read()))
#         except ParserError:
#             continue

#         # toplevel
#         root_name = Path(filename).with_suffix("").name
#         root_title = str(linkmap[0])

#         def grab_links(linkmap):
#             for item in linkmap:
#                 if not isinstance(item, Element):
#                     continue

#                 if item.has_children():
#                     grab_links(item)

#                 href = item.get("href")
#                 targetptr = linkmap.get("targetptr")
#                 if targetptr is not None and href is not None:
#                     text = ""
#                     if linkmap[0].tag == "ttl":
#                         text = str(linkmap[0])
#                     links[f"{targetptr}"] = (root_name, root_title, href, text)

#         grab_links(linkmap)

#     return links


# def create_grph_pth(cmd_path, doc_path):
#     grph_pth = os.path.join(cmd_path, "graphics")
#     if not os.path.isdir(cmd_path):
#         raise FileNotFoundError(
#             f'Invalid documentation path. "graphics" directory does not appear to '
#             "be a directory within the documentation path at:"
#             f"{doc_path}"
#         )
#     return grph_pth

# # first, read the internal version
# def create_GLB_VAL(glb_path):
#     GLB_VAL = {}
#     with open(os.path.join(glb_path, "build_variables.ent"), "r") as fid:
#         lines = fid.read().splitlines()

#     # have to write our own interperter here since this is non-standard lxml
#     for line in lines:
#         entity_names = re.findall(r"!ENTITY (\S*) ", line)
#         if len(entity_names):
#             matches = re.findall(r"'(\S*)'", line)
#             if len(matches):
#                 GLB_VAL[entity_names[0]] = matches[0]
#     return GLB_VAL


# def variables(GLB_VAL):

#     PYMAPDL_CLASS = "ansys.mapdl.generatedcommands"
#     ans_version = GLB_VAL["ansys_internal_version"]
#     base_url = f"https://ansyshelp.ansys.com/Views/Secured/corp/v{ans_version}/en/"
#     cmd_base_url = f"{base_url}/ans_cmd/"

#     return PYMAPDL_CLASS, ans_version, base_url, cmd_base_url


# def load_graphics_fcache(grph_pth):

#     # load all graphics and cache the basename without extension
#     filenames = list(glob.glob(os.path.join(grph_pth, "*"), recursive=True))
#     fcache = {}
#     for filename in filenames:
#         basename = Path(filename).with_suffix("").name
#         if not os.path.isfile(filename):
#             raise FileNotFoundError(f"Unable to locate {basename}")
#         fcache[basename] = os.path.split(filename)[-1]

#     return fcache


# #################################################################
# # FUNCTIONS TO CREATE THE DOC ###################################
# #################################################################

# # globals
# def create_docu_global(glb_path):
#     docu_ent = os.path.join(glb_path, "docu_global.ent")

#     docu_global = {}
#     with open(docu_ent, "r") as fid:
#         lines = fid.read().splitlines()

#         # have to write our own interperter here since this is non-standard lxml
#         for line in lines:
#             entity_names = re.findall(r"!ENTITY (\S*) ", line)
#             if len(entity_names):
#                 entity_name = entity_names[0]

#                 targetdocs = re.findall(r'targetdoc="(\S*)"', line)
#                 targetdoc = targetdocs[0] if len(targetdocs) else None

#                 targetptrs = re.findall(r'targetptr="(\S*)"', line)
#                 targetptr = targetptrs[0] if len(targetptrs) else None

#                 citetitles = re.findall(r"<citetitle>&(\S*);</citetitle>", line)
#                 citetitle = citetitles[0] if len(citetitles) else None

#                 docu_global[entity_name] = (targetdoc, targetptr, citetitle)

#     return docu_global


# def create_terms_global(GLB_VAL, glb_path):
#     terms_global = GLB_VAL.copy()
#     with open(os.path.join(glb_path, "terms_global.ent"), "r") as fid:
#         lines = fid.read().splitlines()

#         for line in lines:
#             entity_names = re.findall(r"!ENTITY (\S*) ", line)
#             if len(entity_names):
#                 entity_name = entity_names[0]

#                 text = re.findall(r"'(.*)'", line)
#                 if len(text):
#                     terms_global[entity_name] = text[0]

#     # Adding manually terms_globals value from warnings.
#     terms_global["sgr"] = ":math:`\sigma`"
#     terms_global["gt"] = ":math:`\sigma`"
#     terms_global["thgr"] = ":math:`<`"
#     terms_global["phgr"] = ":math:`<`"
#     terms_global["ngr"] = ":math:`\phi`"
#     terms_global["agr"] = ":math:`\alpha`"
#     terms_global["OHgr"] = ":math:`\Omega`"
#     terms_global["phis"] = ":math:`\phi`"
#     terms_global["thetas"] = ":math:`\theta`"

#     # These are supposed to be uploaded automatically from the `character.ent` file
#     terms_global["#13"] = "#13"
#     terms_global["#160"] = "nbsp"
#     terms_global["#215"] = "times"
#     terms_global["#934"] = ":math:`\Phi`"

#     return terms_global


# # THIS IS A HACK!
# def get_links(glb_path):
#     try:
#         links
#     except:
#         links = load_links(glb_path)
#     return links


# # load ansys manuals as well
# def load_ansys_manuals(glb_path, docu_global, links, base_url, fcache, terms_global):
#     # items = []
#     with open(os.path.join(glb_path, "global_files", "ansys.manuals.ent"), "r") as fid:
#         text = fid.read()
#         matches = re.findall(r"ENTITY([\S\s]*?)<!", text)
#         for match in matches:
#             item = Element(fromstring(match)).to_rst(
#                 links=links, base_url=base_url, fcache=fcache
#             )
#             key = item.split()[0]
#             text = item.replace(key, "").strip()
#             if not text.startswith("'"):
#                 continue

#             text = text[1:-2].strip()

#             def term_replacer(match):
#                 term = match.group()[1:-1]
#                 if term in docu_global:
#                     _, key, cite_title = docu_global[term]
#                     if key in links:
#                         root_name, root_title, href, text = links[key]
#                         link = f"{base_url}{root_name}/{href}"
#                         link_text = terms_global.get(cite_title, root_title)
#                         return f"`{link_text} <{link}>`_"
#                 else:
#                     if term not in terms_global:
#                         return match.group()
#                     return terms_global[term]

#             # term_replacer_ = term_replacer(match, links)
#             text = re.sub(r"&[\S]*;", term_replacer, text)

#             terms_global[key] = text
#     return terms_global


# # load special characters
# def load_special_characters(doc_path, terms_global):
#     path = os.path.join(
#         doc_path, "tools/custom_2012/doctypes/ansysdocbook/ent/", "*.ent"
#     )
#     isoams_dat = list(glob.glob(path))
#     for filename in isoams_dat:
#         with open(filename, "r") as fid:
#             lines = fid.read().splitlines()
#             # have to write our own interperter here since this is non-standard lxml
#             for line in lines:
#                 entity_names = re.findall(r"!ENTITY (\S*) ", line)
#                 if len(entity_names):
#                     matches = re.findall(r"<!--(.*)-->", line)
#                     if len(matches):
#                         char_name = matches[0].strip()
#                         try:
#                             terms_global[entity_names[0]] = unicodedata.lookup(
#                                 char_name
#                             )
#                         except KeyError:
#                             continue

#     # This is not working for now, to be improved

#     # filename = os.path.join(
#     #     doc_path, "DITA-Open-Toolkit/lib/xerces-2_11_0.AnsysCustom/docs/dtd/", "characters.ent"
#     # )
#     # with open(filename, "r") as fid:
#     #     lines = fid.read().splitlines()
#     #     # have to write our own interperter here since this is non-standard lxml
#     #     for line in lines:
#     #         entity_names = re.findall(r"!ENTITY (\S*)", line)
#     #         if len(entity_names):
#     #             matches = re.findall(r"#\d\d\d", line)
#     #             if len(matches):
#     #                 char_name = matches[0]
#     #                 try:
#     #                     terms_global[entity_names[0]] = char_name
#     #                 except KeyError:
#     #                     continue

#     return terms_global

# Copyright (c) 2023 ANSYS, Inc. All rights reserved.

import logging
import re
import textwrap
import warnings

from lxml.etree import tostring
from lxml.html import fromstring

CONV_EQN = False
CMD_MAP_GLOB = {}

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

# Map XML command to pycommand function
CMD_MAP = {}

# XML commands to skip
SKIP = {"*IF", "*ELSE", "C***", "*RETURN"}


def to_py_name(name, cmd_map=None):
    """Convert to a Python-compatible name."""
    if cmd_map is not None:
        global CMD_MAP_GLOB
        CMD_MAP_GLOB = cmd_map
    try:
        py_name = CMD_MAP_GLOB[name]
    except:
        py_name = name
        print("not documented : ", name)
    return py_name


# ############################################################################
# AST functions
# ############################################################################


def multireplace(string, replacements, ignore_case=False):
    """Given a string and a replacement map, return the replaced string.

    Parameters
    ----------
    string : str
        String to execute replacements on.

    replacements : dict
        Replacement dictionary {value to find: value to replace}.

    ignore_case : bool, optional
        Whether the match should be case insensitive. The default is ``False``.

    Returns
    -------
    str
        Replaced string.
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
    # should take place.
    # For instance given the replacements {'ab': 'AB', 'abc': 'ABC'} against the string 'hey abc',
    # it should produce 'hey ABC' and not 'hey ABc'
    rep_sorted = sorted(replacements, key=len, reverse=True)
    rep_escaped = map(re.escape, rep_sorted)

    # Create a big OR regex that matches any of the substrings to replace.
    pattern = re.compile("|".join(rep_escaped), re_mode)

    # For each match, look up the new string in the replacements, being the key the normalized
    # old string.
    return pattern.sub(lambda match: replacements[normalize_old(match.group(0))], string)


def split_trail_alpha(text):
    """Split a string based on the last tailing non-alphanumeric character."""
    for ii, char in enumerate(text):
        if not char.isalnum():
            break

    ii += 1

    return text[:ii], text[ii:]


def is_numeric(text):
    """Return ``True`` when a string is numeric."""
    try:
        float(text)
        return True
    except ValueError:
        return False


# ############################################################################
# Element class
# ############################################################################


class Element:
    """Provides the base element."""

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
        """Text content."""
        return self._element.text_content()

    @property
    def raw(self):
        """Raw string of the element."""
        return tostring(self._element).decode()

    @property
    def tostring(self):
        """Attributes of the element as a dictionary."""
        return tostring(self._element)

    def has_children(self):
        """Return wether the element has children."""
        return bool(len(self._element.getchildren()))

    def get(self, entry):
        """Get an item from an element."""
        return self._element.get(entry)

    @property
    def added(self):
        """Has the revision flag ``added``."""
        return self.get("revisionflag") == "added"

    @property
    def any_isalnum(self):
        """Returns ``True`` if any characters are alphanumeric."""
        return any([char.isalnum() for char in str(self)])

    @property
    def tail(self):
        """Tail of the element as a string."""
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
        """Element title."""
        return self.find("Title")

    @property
    def content(self):
        """Text content."""
        return self._content

    def __repr__(self):
        return "".join([str(item) for item in self._content])

    @property
    def id(self):
        """ID of the element."""
        return self._element.get("id")

    def to_rst(self, prefix="", links=None, base_url=None, fcache=None):
        """Return a string to enable converting the element to an RST format."""
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

    def rec_find(self, _type, terms=None):
        """Find the first type matching a given type string recursively."""
        for item in self:
            if type(item).__name__ == _type:
                if _type == "Refname" or _type == "Refnamediv":
                    item.terms = terms
                return item
            if isinstance(item, Element):
                subitem = item.rec_find(_type)
                if subitem is not None:
                    return subitem
        return None

    def find(self, _type, terms=None):
        """Find the first type matching a given type string."""
        for item in self:
            if type(item).__name__ == _type:
                if _type == "Refname" or _type == "Refnamediv":
                    if terms == None:
                        print("ERROR: terms not defined for a Refname class")
                    item.terms = terms
                return item
        return None

    def find_all(self, _type, recursive=False, terms=None):
        """Find all types matching a given type string."""
        items = []
        for item in self:
            if type(item).__name__ == _type:
                if _type == "Refname" or _type == "Refnamediv":
                    item.terms = terms
                items.append(item)
            elif recursive and isinstance(item, Element):
                items.extend(item.find_all(_type))

        return items

    @property
    def next_elem(self):
        """Next element."""
        elem = self._element.getnext()
        return parse_element(elem) if elem is not None else elem

    @property
    def prev_elem(self):
        """Previous element."""
        elem = self._element.getprevious()
        return parse_element(elem) if elem is not None else elem

    @property
    def tag(self):
        """Element tag."""
        return self._element.tag


class ItemizedList(Element):
    """Provides the itemized list element."""

    def __repr__(self):
        return "\n".join([f"* {str(item).strip()}" for item in self])

    def to_rst(self, prefix="", links=None, base_url=None, fcache=None):
        """Return a string to enable converting the element to an RST format."""
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
    """Provides the simple itemized list element."""

    def __repr__(self):
        return "\n".join([f"* {str(item).strip()}" for item in self])


class Member(Element):
    """Provides the member element for a simple itemized list."""

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
    """Provides the ordered list element."""

    def to_rst(self, prefix="", links=None, base_url=None):
        """Return a string to enable converting the element to an RST format."""
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
    """Provides the list item element."""

    def to_rst(self, prefix="", links=None, base_url=None, fcache=None):
        """Return a string to enable converting the element to an RST format."""
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
    """Provides the filename element."""

    def to_rst(self, prefix=""):
        """Return a string to enable converting the element to an RST format."""
        return f"``{self[0]}`` {self.tail}"


class OLink(Element):
    """Provides the external link element."""

    def __init__(self, element):
        super().__init__(element)

    @property
    def targetptr(self):
        """Value for the ``targetptr`` contained in the OLink element."""
        return self.get("targetptr")

    @property
    def targetdoc(self):
        """Value for the ``targetdoc`` parameter contained in the OLink element."""
        return self.get("targetdoc")

    def to_rst(self, prefix="", links=None, base_url=None):
        """Return a string to enable converting the element to an RST format."""
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
    """Provides the paragraph element."""

    def __repr__(self):
        lines = [""]
        lines.append(" ".join([str(item) for item in self._content]))
        lines.append("\n")
        return "".join(lines)

    def to_rst(self, prefix="", links=None, base_url=None, fcache=None):
        """Return a string to enable converting the element to an RST format."""
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
    """Provides the phrase element."""

    def __repr__(self):
        return " ".join([str(item) for item in self._content])


class Structname(Element):
    """Provides the structure name element."""

    pass


class Title(Element):
    """Provides the title element."""

    def __repr__(self):
        return " ".join([str(item) for item in self._content]) + "\n"


class Emphasis(Element):
    """Provides the emphasis element."""

    @property
    def role(self):
        """Return the role parameter value contained in the Emphasis element."""
        return self._element.get("role")

    def to_rst(self, prefix="", links=None, base_url=None):
        """Return a string to enable converting the element to an RST format."""

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
    """Provides the example element."""

    # def source(self):
    #     """The program listing of the documentation."""
    #     for item in self._content:
    #         if isinstance(item, ProgramListing):
    #             return item
    #     return ""
    pass


class InformalExample(Element):
    """Provides the informal example element."""

    def __repr__(self):
        lines = ["\n"]
        if self.title:
            lines.append(f"Example:\n")
        else:
            lines.append(f"Example: {self.title}\n")
        lines.extend([f"{line}" for line in self._content])  # self._content.splitlines()
        return "\n".join(lines)


class GuiMenu(Element):
    """Provides the GUI menu element."""

    pass


class Replaceable(Element):
    """Provides the replaceable element."""

    @property
    def is_equals(self):
        """Replaceable equals something."""
        # return self.tail.startswith("=")
        return False

    @property
    def content_equals(self):
        """Content of the element after handling the '=' sign."""
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
        """Return a string to enable converting the element to an RST format."""
        if isinstance(self.prev_elem, Command):
            if any([self.content[0] in arg for arg in self.prev_elem.args]):
                return f"{self.tail}"
        if self.is_equals:
            return self.content_equals
        return f"``{self.content[0]}`` {self.tail}"


class ProgramListing(Element):
    """Provides the program listing element."""

    @property
    def source(self):
        """Return the source value."""
        if self._element.text is None:
            return "\n".join(str(item) for item in self.content)
        return self._element.text

    def to_rst(self, prefix=""):
        """Return a string to enable converting the element to an RST format."""
        header = f"\n\n{prefix}.. code::\n\n"
        return header + textwrap.indent(self.source, prefix + " " * 3) + "\n"


class Variablelist(Element):
    """Provides the variable list."""

    def to_rst(self, prefix="", links=None, base_url=None, fcache=None):
        """Return a string to enable converting the element to an RST format."""
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
        """List containing the terms of the element."""
        return [str(item.term) for item in self if isinstance(item, VarlistEntry)]


class RefSection(Element):
    """Provides the reference section element."""

    def to_rst(self, prefix="", links=None, base_url=None, fcache=None):
        """Return a string to enable converting the element to an RST format."""
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
    """Provides the variable list entry element."""

    @property
    def parm_types(self):
        """One or more parameter types.

        This is guessed from any subvarlists. If unavailable, then it's guessed
        from the description of the variable.

        This is either a string, float, or integer (or some combination thereof).

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
        """Term of the element."""
        return self.content[0]

    @property
    def text(self):
        """Text of the element."""
        return self.content[1]

    def py_term(self, links=None, base_url=None):
        """Python-compatible term."""
        if self.is_arg:
            arg = str(self.term).lower()

            if arg == "type":
                arg = "type_"

            if self.parm_types is not None:
                ptype_str = " or ".join([parm_type.__name__ for parm_type in self.parm_types])

                return f"{arg} : {ptype_str}"
            return f"{arg}"

        if self.term.tag in item_needing_links_base_url:
            arg = self.term.to_rst(links=links, base_url=base_url).replace("--", "").strip()
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
        """Return if this argument is active."""
        if not self.is_arg:
            return True

        # Otherwise, simply check for any alphanumeric characters in the
        # term. Normally these terms are just '--' or '--,--'
        return self.term.any_isalnum

    @property
    def is_arg(self):
        """Return ``True`` when this variable list is for an argument."""
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
        """Return a string to enable converting the element to an RST format."""
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
    """Provides the term element."""

    def to_rst(self, prefix="", links=None, base_url=None, fcache=None):
        """Return a string to enable converting the element to an RST format."""

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
    """Provides the GUI label element."""

    pass


class GuiMenuItem(Element):
    """Provides the GUI menu item element."""

    pass


class SuperScript(Element):
    """Provides the superscript element."""

    def to_rst(self, prefix=""):
        """Return a string to enable converting the element to an RST format."""
        return f":sup:`{self.content[0]}` {self.tail}"


class Code(Element):
    """Provides the code element."""

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
        """Return the equation related to the math element."""
        return self.content[0][1:-1]


class Math(_Math):
    """Provides the math element."""

    def to_rst(self, prefix=""):
        """Return a string to enable converting the element to an RST format."""
        lines = ["", "", f"{prefix}.. math::\n"]
        lines.append(textwrap.indent(self.equation, prefix=prefix + " " * 4))
        lines.append("")
        return "\n".join(lines)


class InlineEquation(_Math):
    """Provides the inline equation element."""

    def __init__(self, element):
        self._element = element
        self._content = []
        self._parse_equation(element.find("math"))

    @property
    def tail(self):
        """Return the tail of the element as a string."""
        return self.raw.split("</inlineequation>")[-1].replace("\n", "")

    def to_rst(self, prefix=""):
        """Return a string to enable converting the element to an RST format."""
        return f":math:`{self.equation.strip()}` {self.tail}"


class SubScript(Element):
    """Provides the subscript element."""

    def __init__(self, element):
        super().__init__(element)


class InlineGraphic(Element):
    """Provides the inline graphic element."""

    def fileref(self):
        """File reference."""
        return self._element.get("fileref")


class Quote(Element):
    """Provides the quote element."""

    def __init__(self, element):
        super().__init__(element)
        # self._content[0] = f"{self._content[0]}"

    @property
    def quote(self):
        """Quote value."""
        return self[0]

    def __repr__(self):
        return f'"{self.quote}" {self.tail}'


class Link(Element):
    """Provides the link element."""

    def __init__(self, element):
        super().__init__(element)
        self._linkend = element.get("linkend")

    @property
    def linkend(self):
        """Link."""
        return self._linkend

    def __repr__(self):
        return str(self.linkend)

    def to_rst(self, prefix="", links=None, base_url=None):
        """Return a string to enable converting the element to an RST format."""
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
    """Provides the cross reference element."""

    @property
    def tail(self):
        """Tail of the element as a string."""
        return " ".join([str(item) for item in self._content])

    def to_rst(self, prefix=""):
        """Return a string to enable converting the element to an RST format."""
        # disabled at the moment
        # return f':ref:`{self.linkend}`{self.tail}'
        return self.tail


class UserInput(Element):
    """Provides the user input element."""

    pass


class Screen(Element):
    """Provides the screen element."""

    pass


class Literal(Element):
    """Provides the literal output element."""

    def to_rst(self, prefix=""):
        """Return a string to enable converting the element to an RST format."""
        return f"``{self.content[0]}`` {self.tail}"


class Caution(Element):
    """Provides the caution element."""

    def to_rst(self, prefix=""):
        """Return a string to enable converting the element to an RST format."""
        lines = ["", "", ".. warning::"]
        lines.append(textwrap.indent(str(self), prefix=prefix + "   "))
        return "\n".join(lines)


class Graphic(Element):
    """Provides the graphic element."""

    @property
    def entityref(self):
        """Value of the ``entityref`` parameter contained in the graphic element."""
        entityref = self.get("entityref")
        if entityref is not None:
            entityref = entityref.strip()
        return entityref

    def to_rst(self, fcache, prefix=""):
        """Return a string to enable converting the element to an RST format."""

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
    """Provides the function element."""

    pass


class Note(Element):
    """Provides the note element."""

    pass


class BlockQuote(Element):
    """Provides the block quote element."""

    def to_rst(self, prefix="", links=None, base_url=None, fcache=None):
        """Return a string to enable converting the element to an RST format."""
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
    """Provides the reference metadata element."""

    @property
    def refentry_title(self):
        """Title of the referency entry."""
        title = self.rec_find("Refentrytitle")
        if title is not None:
            title = str(title).strip()
        else:
            title = ""
        return title


class IndexTerm(Element):
    """Provides the index term element."""

    pass


class Primary(Element):
    """Provides the primary element."""

    pass


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
    """Provides the tgroup element, which contains the header and body rows of a table."""

    @property
    def n_col(self):
        """Number of columns."""
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
        """List of the rows in the TBody."""
        return self.find("TBody").find_all("Row")

    def to_rst(self, prefix="", links=None, base_url=None):
        """Return a string to enable converting the element to an RST format."""
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
    """Provides the table element"""

    @property
    def title(self):
        """Table title."""
        return self.find("Title")

    @property
    def tgroup(self):
        """TGroup."""
        return self.find("TGroup")

    def to_rst(self, prefix="", links=None, base_url=None):
        """Return a string to enable converting the element to an RST format."""
        lines = []
        if self.title is not None:
            lines.append(f"{self.title}".strip())
            lines.append((len(lines[-1]) * "="))
            lines.append("")

        if self.tgroup is not None:
            a = self.tgroup
            lines.append(a.to_rst(prefix=prefix, links=links, base_url=base_url))

        return "\n".join(lines)

    def __repr__(self):
        # This method is limited as the links and the base_url are skiped.
        return self.to_rst(links={}, base_url=f"pass")


class Refentrytitle(Element):
    """Provides the title of the reference entry."""

    def __repr__(self):
        items = []
        for item in self._content:
            item = str(item)
            for key, value in CONST.items():
                item = item.replace(key, value)
            items.append(item)
        return "".join(items)


class Refnamediv(Element):
    """Provides the refnamediv element, which contains the name,
    purpose, and classification of a reference."""

    def __init__(self, element, terms=None):
        self._element = element
        self._terms = terms
        super().__init__(element)

    @property
    def terms(self):
        """Terms of the element."""
        return self._terms

    @terms.setter
    def terms(self, terms):
        """Set the terms of the element."""
        self._terms = terms

    @property
    def refname(self):
        """Refname of the element."""
        return self.find("Refname", self._terms)

    @property
    def purpose(self):
        "Refpurpose of the element."
        return self.find("Refpurpose")


class Refname(Element):
    """Provides the refname element which contains
    the name of a reference."""

    def __init__(self, element, terms=None):
        self._element = element
        self._terms = terms
        super().__init__(element)

    @property
    def terms(self):
        """Terms of the element."""
        return self._terms

    @terms.setter
    def terms(self, terms):
        """Set the terms of the element."""
        self._terms = terms

    @property
    def raw_args(self):
        """Raws containing the command arguments."""
        cmd = str(self)
        cmd = cmd.replace("&fname_arg;", self._terms["fname_arg"])
        cmd = cmd.replace("&fname1_arg;", self._terms["fname1_arg"])
        cmd = cmd.replace("&fname2_arg;", self._terms["fname2_arg"])
        cmd = cmd.replace("&pn006p;", self._terms["pn006p"])
        cmd = cmd.replace("&ansysBrand;", self._terms["ansysBrand"])
        split_args = cmd.split(",")[1:]
        return split_args

    @property
    def args(self):
        """Command arguments."""
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

            # simply check if we can use this as a valid Python kwarg
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
    """Provides the refpurpose element, which contains
    a short synopsis of a reference."""

    def __repr__(self):
        return " ".join([str(item) for item in self._content])


class Refclass(Element):

    pass


class Application(Element):

    pass


class Refsect1(Element):

    pass


class Command(Element):
    """Provides the command element."""

    @property
    def command(self):
        """Name of the command."""
        return self[0]

    @property
    def tail_no_args(self):
        """Tail of the element after removing all its arguments."""
        tail = self.tail
        for arg in self.args:
            tail = tail.replace(arg, "")
        return tail

    def __repr__(self):
        return f"{self.command} {self.tail}"

    @property
    def has_args(self):
        """Return whether the element has arguments."""
        # return self.tail.startswith(",")
        return False  # TODO: This is to be modified

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
        """String containing the arguments of the element."""
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
        """Pythonic name of the command."""
        return to_py_name(self.command)

    @property
    def sphinx_cmd(self):
        """String to refer to the Python command with Sphinx."""
        if self.py_cmd == self.command:
            ref = f"``self.py_cmd``"
        else:
            ref = f":ref:`{self.py_cmd}`"
        return ref

    def to_rst(self, prefix=""):
        """Return a string to enable converting the element to an RST format."""
        if self.args and self.args[0] != "":
            return f"{self.sphinx_cmd} {self.tail_no_args}"
        else:
            return f"{self.sphinx_cmd} {self.tail}"


class ComputerOutput(Element):
    """Provides the computer output element."""

    def to_rst(self, prefix=""):
        """Return a string to enable converting the element to an RST format."""
        return f"``{self[0]}`` {self[1]}"


class Figure(Element):
    """Provides the figure element."""

    @property
    def title(self):
        """First title element found in the figure element."""
        return self.rec_find("Title")

    @property
    def graphic(self):
        """First graphic element found in the figure element."""
        return self.rec_find("Graphic")

    def to_rst(self, prefix="", fcache=None):
        """Return a string to enable converting the element to an RST format."""
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


class GuiButton(Element):

    pass


class GuiIcon(Element):

    pass


class Highlights(Element):

    pass


class Important(Element):

    pass


class InformalEquation(Element):

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


class InformalFigure(Element):

    pass


class Envar(Element):

    pass


class ImageData(Element):

    pass


class ColSpec(Element):

    pass


class TBody(Element):
    """Provides the tbody element."""

    @property
    def rows(self):
        """ "Return all the row elements found in the TBody element."""
        return self.find_all("Row")

    def to_rst(self, l_head, prefix="", links=None, base_url=None):
        """Return a list to enable converting the element to an RST format."""
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
    """Provides the entry element."""

    @property
    def morerows(self):
        """Value for the ``morerows`` parameter contained in the entry element."""
        return self._element.get("morerows")

    def to_rst(self, prefix="", links=None, base_url=None, fcache=None):
        """Return a string to enable converting the element to an RST format."""

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
    """Provides the row element."""

    @property
    def entry(self):
        """Return all entry elements found in the row element."""
        return self.find_all("Entry")

    def to_rst_list(self, prefix="", links=None, base_url=None):
        """Return a list to enable converting the element to an RST format."""
        row = []
        for entry in self.entry:
            content = entry.to_rst(links=links, base_url=base_url)
            content = content.replace("\n", "")
            content = content.replace("\r", "")
            row.append(content)
        return row


class THead(Element):
    """Provides the thead element."""

    @property
    def rows(self):
        """Return all row elements found in the THead element."""
        return self.find_all("Row")

    def to_rst(self, prefix="", links=None, base_url=None):
        """Return a list and the length of the list for converting the element
        to an RST format."""

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
    """Provides the chapter element."""

    @property
    def helpstring(self):
        """Value for the ``helpstring`` parameter contained in the chapter element."""
        return self[1]._element.get("helpstring")

    def __repr__(self):
        items = [f"Chapter {self.helpstring}\n\n"]
        items.extend([str(item) for item in self._content])
        return "".join(items)


class Section1(Element):

    pass


class ProductName(Element):

    pass


class XMLCommand(Element):
    """Provides the XML command from the documentation."""

    def __init__(
        self,
        filename,
        terms,
        docu_global,
        version_variables,
        links,
        fcache,
        meta_only=False,
    ):
        """Parse command from XML file."""
        self._xml_filename = filename
        self._terms = terms
        self._docu_global = docu_global
        self._autogenerated_directory_name = version_variables.autogenerated_directory_name
        self._links = links
        self._base_url = version_variables.base_url
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
        """Source filename of the command."""
        return self._xml_filename

    @property
    def args(self):
        """Command arguments."""
        return self._refname_div.refname.args

    @property
    def default(self):
        """Command default."""
        if self._refsynopsis:
            for item in self._refsynopsis:
                if str(item.title).strip() == "Command Default":
                    return item

    @property
    def arg_desc(self):
        """Each argument's description."""
        refsyn = self.rec_find("Refsynopsisdiv")

        # search by ID
        if refsyn is None:
            for elem in self.find_all("RefSection"):
                if elem.id is not None and "argdescript" in elem.id:
                    return elem

        return refsyn

    @property
    def short_desc(self):
        """Short description of the command."""
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
        """Name of the XML command."""
        return self._metadata.refentry_title

    @property
    def py_name(self):
        """Python-compatible name."""
        return to_py_name(self.name)

    @property
    def py_args(self):
        return [arg.lower() for arg in self.args]

    @property
    def py_signature(self):
        """Beginning of the Python command's definition."""
        args = ["self"]
        kwargs = [f'{arg}=""' for arg in self.py_args if "--" not in arg]
        arg_sig = ", ".join(args + kwargs)
        return f"def {self.py_name}({arg_sig}, **kwargs):"

    def py_docstring(self, custom_functions):
        """Python docstring of the command."""
        xml_cmd = f"{self._terms['pn006p']} Command: `{self.name} <{self.url}>`_"

        items = [self.short_desc, "", xml_cmd]

        if self.default is not None:
            if self.default.tag in item_needing_links_base_url:
                items += [""] + textwrap.wrap(
                    "Default: " + self.default.to_rst(links=self._links, base_url=self._base_url)
                )
            else:
                items += [""] + textwrap.wrap("Default: " + self.default.to_rst())
        if self.args is not None:
            items += [""] + self.py_parm
        if custom_functions is not None and (
            self.py_name in custom_functions.py_names
            and self.py_name in custom_functions.py_returns
        ):
            items += [""] + custom_functions.py_returns[self.py_name]
        if self.notes is not None:
            items += [""] + self.py_notes
        if custom_functions is not None and (
            self.py_name in custom_functions.py_names
            and self.py_name in custom_functions.py_examples
        ):
            items += [""] + custom_functions.py_examples[self.py_name]
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

        # sub XML command args
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

            return f":func:`{func}({py_args}) <{self._autogenerated_directory_name}.{func}>` {tail}"

        # command replacement with args
        docstr = re.sub(
            r"<CMD>[a-z0-9]*</CMD>?(\s*,+\s*[A-Za-z0-9%`]*)+",
            arg_replacer,
            docstr,
        )

        def cmd_replacer(match):
            func = match.group().replace("<CMD>", "").replace("</CMD>", "")
            return f":func:`{func}() <{self._autogenerated_directory_name}.{func}>`"

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
                    link_text = self._terms.get(cite_title, root_title)
                    return f"`{link_text} <{link}>`_"
            else:
                if term not in self._terms:
                    warnings.warn(f"term {term} not in terms")
                    return ""
                return self._terms[term]

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
        """Python-formatted notes string."""
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
        """Python parameter's string."""
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
        """URL to the Ansys command documentation."""
        cmd_base_url = f"{self._base_url}/ans_cmd/"
        return f"{cmd_base_url}{self.filename}"

    @property
    def filename(self):
        """Command filename"""
        return self[0]._element.get("filename")

    @property
    def _refname_div(self):
        return self.rec_find("Refnamediv", self._terms)

    @property
    def _refsynopsis(self):
        return self.find("Refsynopsisdiv")

    @property
    def notes(self):
        """Notes of the command."""
        for item in self:
            if str(item.title).strip() == "Notes":
                return item

    def __repr__(self):
        lines = [f"Original command: {self.name}"]
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

    def py_source(self, custom_functions=None, cmd_map=None):
        """Return the Python source."""

        if cmd_map is not None:
            global CMD_MAP_GLOB
            CMD_MAP_GLOB = cmd_map

        if custom_functions is None or self.py_name not in custom_functions.py_names:

            if len(self.py_args) > 0:
                command = 'command = f"' + self.name + ",{" + "},{".join(self.py_args) + '}"\n'
            else:
                command = 'command = f"' + self.name + '"\n'
            return_command = "return self.run(command, **kwargs)\n"
            source = textwrap.indent("".join([command, return_command]), prefix=" " * 4)

        else:
            source = "".join(custom_functions.py_code[self.py_name])
        return source

    def to_python(self, cmd_map, custom_functions=None, prefix=""):
        """Return the complete Python definition of the command."""

        global CMD_MAP_GLOB
        CMD_MAP_GLOB = cmd_map

        docstr = textwrap.indent(
            f'\nr"""{self.py_docstring(custom_functions)}\n"""', prefix=prefix + " " * 4
        )
        if custom_functions is not None and self.py_name in custom_functions.lib_import:
            out = f"{''.join(custom_functions.lib_import[self.py_name])}\n{self.py_signature}{docstr}\n{self.py_source(custom_functions)}"  # noqa : E501
        else:
            out = f"{self.py_signature}{docstr}\n{self.py_source(custom_functions)}"
        return out


class InformalTable(Element):
    """Provides the informal table element."""

    def to_rst(self, prefix=""):
        """Return a string to enable converting the element to an RST format."""
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
    "informalfigure": InformalFigure,
    "classname": ClassName,
    "computeroutput": ComputerOutput,
    "figure": Figure,
    "footnote": Footnote,
    "footnoteref": Footnoteref,
    "formalpara": Formalpara,
    "glossterm": Glossterm,
    "guibutton": GuiButton,
    "guiicon": GuiIcon,
    "highlights": Highlights,
    "important": Important,
    "informalequation": InformalEquation,
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
    "informalfigure": InformalFigure,
    "variablelist": Variablelist,
    "blockquote": BlockQuote,
    "informalequation": InformalEquation,
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
    """Provides for loading an XML file as an AST (abstract syntax tree)."""

    def __init__(self, filename, meta_only=False):
        """Parse command from XML file."""
        self._xml_filename = filename
        root = fromstring(open(filename, "rb").read())

        # parse the file
        super().__init__(root, parse_children=not meta_only)

    @property
    def xml_filename(self):
        """Source filename of the command."""
        return self._xml_filename

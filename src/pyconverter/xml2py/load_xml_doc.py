# Copyright (c) 2023 ANSYS, Inc. All rights reserved.

import glob
import os
from pathlib import Path
import re
import unicodedata

from lxml.etree import ParserError
from lxml.html import fromstring
import pyconverter.xml2py.ast_tree as ast
import pyconverter.xml2py.version_variables as var
from tqdm import tqdm


def load_links(link_path):
    """Load all links.

    Parameters
    ----------
    link_path : str
        Path to the links directory.

    Returns
    -------
    links : dict
        Dictionary containing the link names and the needed information to render the links.

    """

    db_path = os.path.join(link_path, "*.db")
    linkmap_fnames = list(glob.glob(db_path, recursive=True))
    links = {}

    for filename in tqdm(linkmap_fnames, desc="Loading links"):
        try:
            linkmap = ast.Element(fromstring(open(filename, "rb").read()))
        except ParserError:
            continue

        # toplevel
        root_name = Path(filename).with_suffix("").name
        root_title = str(linkmap[0])

        def grab_links(linkmap):
            for item in linkmap:
                if not isinstance(item, ast.Element):
                    continue

                if item.has_children():
                    grab_links(item)

                href = item.get("href")
                targetptr = linkmap.get("targetptr")
                if targetptr is not None and href is not None:
                    text = ""
                    if linkmap[0].tag == "ttl":
                        text = str(linkmap[0])
                    links[f"{targetptr}"] = (root_name, root_title, href, text)

        grab_links(linkmap)

    return links


def load_fcache(graph_path):
    """Load all graphics and cache the base name without the extension.

    Parameters
    ----------
    graph_path : str
        Path to the graphic directory.

    Returns
    -------
    fcache : dict
        Dictionary containing the base names of the graphics and their path.

    """

    filenames = list(glob.glob(os.path.join(graph_path, "*"), recursive=True))
    fcache = {}
    for filename in filenames:
        basename = Path(filename).with_suffix("").name
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"Unable to locate {basename}")
        fcache[basename] = os.path.split(filename)[-1]

    return fcache


def load_docu_global(term_path):
    """Load all global documents.

    Parameters
    ----------
    term_path : str
        Path to the terms directory.

    Returns
    -------
    docu_global : dict
        Dictionary containing the entity names from the documentation and their path.

    """

    docu_ent = os.path.join(term_path, "glb", "docu_global.ent")

    docu_global = {}
    with open(docu_ent, "r") as fid:
        lines = fid.read().splitlines()

        # have to write our own interperter here since this is non-standard lxml
        for line in lines:
            entity_names = re.findall(r"!ENTITY (\S*) ", line)
            if len(entity_names):
                entity_name = entity_names[0]

                targetdocs = re.findall(r'targetdoc="(\S*)"', line)
                targetdoc = targetdocs[0] if len(targetdocs) else None

                targetptrs = re.findall(r'targetptr="(\S*)"', line)
                targetptr = targetptrs[0] if len(targetptrs) else None

                citetitles = re.findall(r"<citetitle>&(\S*);</citetitle>", line)
                citetitle = citetitles[0] if len(citetitles) else None

                docu_global[entity_name] = (targetdoc, targetptr, citetitle)

    return docu_global


def load_terms(
    term_path,
    docu_global,
    links,
    fcache,
    variable_file="build_variables.ent",
    global_terms_file="terms_global.ent",
    manual_file="manuals.ent",
    character_directory="ent",
):

    """Load all needed terms.

    Parameters
    ----------
    term_path : str
        Path to the terms directory.

    docu_global : dict
        Dictionary containing the entity names from the documentation and their path.

    links : dict
        Dictionary containing the link names and the needed information to render the links.

    fcache : dict
        Dictionary containing the base names of the graphics and their path.

    variable_file : str, optional
        Name of the file containing the variable terms to import.
        The default value is ``"build_variables.ent"``.

    global_terms_file : str, optional
        Name of the file containing the global terms to import.
        The default is ``"terms_global.ent"``.

    manual_file : str, optional
        Name of the file containing the manual entities to import.
        The default is ``"manuals.ent"``.

    character_directory : str, optional
        Name of the directory containg the entities for the special characters.
        The default is ``"ent"``.

    Returns
    -------
    terms : dict
        Dictionary containing the entity names and their values.

    """

    terms = {}

    variable_path = os.path.join(term_path, "glb", variable_file)
    if os.path.isfile(variable_path):
        with open(variable_path, "r") as fid:
            lines = fid.read().splitlines()

        # have to write our own interperter here since this is non-standard lxml
        for line in lines:
            entity_names = re.findall(r"!ENTITY (\S*) ", line)
            if len(entity_names):
                matches = re.findall(r"'(\S*)'", line)
                if len(matches):
                    terms[entity_names[0]] = matches[0]

    else:
        print("WARNING: No file found for defining variable terms.")
        # This is done manually. To be improved.
        terms["ansys_internal_version"] = "23.2"

    version_variables = var.Autogenerateddirectory(terms)
    base_url = version_variables.base_url

    global_terms_path = os.path.join(term_path, "glb", global_terms_file)
    if os.path.isfile(global_terms_path):
        with open(global_terms_path, "r") as fid:
            lines = fid.read().splitlines()

            for line in lines:
                entity_names = re.findall(r"!ENTITY (\S*) ", line)
                if len(entity_names):
                    entity_name = entity_names[0]

                    text = re.findall(r"'(.*)'", line)
                    if len(text):
                        terms[entity_name] = text[0]
    else:
        print("WARNING: No file found for defining global terms.")

    # Manually adding terms value from warnings.
    terms["sgr"] = ":math:`\sigma`"
    terms["gt"] = ":math:`\sigma`"
    terms["thgr"] = ":math:`<`"
    terms["phgr"] = ":math:`<`"
    terms["ngr"] = ":math:`\phi`"
    terms["agr"] = ":math:`\alpha`"
    terms["OHgr"] = ":math:`\Omega`"
    terms["phis"] = ":math:`\phi`"
    terms["thetas"] = ":math:`\theta`"

    # These are supposed to be uploaded automatically from the `character.ent` file
    terms["#13"] = "#13"
    terms["#160"] = "nbsp"
    terms["#215"] = "times"
    terms["#934"] = ":math:`\Phi`"

    # load manuals
    manual_path = os.path.join(term_path, "glb", manual_file)
    if os.path.isfile(manual_path):
        with open(manual_path, "r") as fid:
            text = fid.read()
            matches = re.findall(r"ENTITY([\S\s]*?)<!", text)
            for match in matches:
                item = ast.Element(fromstring(match)).to_rst(
                    links=links, base_url=base_url, fcache=fcache
                )
                key = item.split()[0]
                text = item.replace(key, "").strip()
                if not text.startswith("'"):
                    continue

                text = text[1:-2].strip()

                def term_replacer(match):
                    term = match.group()[1:-1]
                    if term in docu_global:
                        _, key, cite_title = docu_global[term]
                        if key in links:
                            root_name, root_title, href, text = links[key]
                            link = f"{base_url}{root_name}/{href}"
                            link_text = terms.get(cite_title, root_title)
                            return f"`{link_text} <{link}>`_"
                    else:
                        if term not in terms:
                            return match.group()
                        return terms[term]

                # term_replacer_ = term_replacer(match, links)
                text = re.sub(r"&[\S]*;", term_replacer, text)

                terms[key] = text
    else:
        print("WARNING: No file found for defining terms.")

    # load special characters
    ent_dir = os.path.join(term_path, "ent")
    if os.path.isdir(ent_dir):
        isoams_dat = list(glob.glob(os.path.join(ent_dir, "*.ent")))
        for filename in isoams_dat:
            with open(filename, "r") as fid:
                lines = fid.read().splitlines()
                # have to write our own interperter here since this is non-standard lxml
                for line in lines:
                    entity_names = re.findall(r"!ENTITY (\S*) ", line)
                    if len(entity_names):
                        matches = re.findall(r"<!--(.*)-->", line)
                        if len(matches):
                            char_name = matches[0].strip()
                            try:
                                terms[entity_names[0]] = unicodedata.lookup(char_name)
                            except KeyError:
                                continue

    else:
        print("WARNING: No entitiy directory.")

    # This is not working for now
    # TODO

    # filename = os.path.join(
    #     doc_path, "DITA-Open-Toolkit/lib/xerces-2_11_0.AnsysCustom/docs/dtd/", "characters.ent"
    # )
    # with open(filename, "r") as fid:
    #     lines = fid.read().splitlines()
    #     # have to write our own interperter here since this is non-standard lxml
    #     for line in lines:
    #         entity_names = re.findall(r"!ENTITY (\S*)", line)
    #         if len(entity_names):
    #             matches = re.findall(r"#\d\d\d", line)
    #             if len(matches):
    #                 char_name = matches[0]
    #                 try:
    #                     terms[entity_names[0]] = char_name
    #                 except KeyError:
    #                     continue

    return terms, version_variables

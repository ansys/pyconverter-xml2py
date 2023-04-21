# import folder_format as ff
import glob
from pathlib import Path

import dita_ast as ast
from lxml.etree import ParserError
from lxml.html import fromstring
import tqdm


def load_links(link_path):
    """Load all links."""

    linkmap_fnames = list(glob.glob(link_path, recursive=True))
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


def load_fcache():
    pass


def load_terms_global():
    pass

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

from typing import Any, Dict, Literal

def cmlist(
    self,
    name: str = "",
    key: str = "",
    entity: Literal["VOLU", "AREA", "LINE", "KP", "ELEM", "NODE", ""] = "",
    **kwargs: Dict[Any, Any],
) -> None:
    """Lists the contents of a component or assembly.

    APDL Command: CMLIST

    Parameters
    ----------
    name
        Name of the component or assembly to be listed (if blank, list all
        selected components and assemblies). If Name is specified, then
        Entity  is ignored.

    key
        Expansion key:

        0
            Do not list individual entities in the component.

        1 or EXPA
            List individual entities in the component.

    entity
        If Name is blank, then the following entity types can be specified:

        VOLU
            List the volume components only.

        AREA
            List the area components only.

        LINE
            List the line components only.

        KP
            List the keypoint components only

        ELEM
            List the element components only.

        NODE
            List the node components only.

    Notes
    -----
    This command is valid in any processor.  For components, it lists the
    type of geometric entity. For assemblies, it lists the components
    and/or assemblies that make up the assembly.

    Examples of possible usage:
    """
    command = f"CMLIST,{name},{key},{entity}"
    return self.run(command, **kwargs)
import parse


def kdist(self, kp1="", kp2="", **kwargs) -> list:
    """Calculates and lists the distance between two keypoints.

    APDL Command: KDIST

    Parameters
    ----------
    kp1
        First keypoint in distance calculation.
    kp2
        Second keypoint in distance calculation.

    Returns
    -------
    list
        ``[DIST, X, Y, Z]`` distance between two keypoints.

    Notes
    -----
    KDIST lists the distance between keypoints KP1 and KP2, as
    well as the current coordinate system offsets from KP1 to KP2,
    where the X, Y, and Z locations of KP1 are subtracted from the
    X, Y, and Z locations of KP2 (respectively) to determine the
    offsets.  KDIST is valid in any coordinate system except
    toroidal [CSYS,3].
    This command is valid in any processor.

    Examples
    --------
    Compute the distance between two keypoints.

    >>> kp0 = (0, 10, -3)
    >>> kp1 = (1, 5, 10)
    >>> knum0 = mapdl.k("", *kp0)
    >>> knum1 = mapdl.k("", *kp1)
    >>> dist = mapdl.kdist(knum0, knum1)
    >>> dist
    [13.96424004376894, 1.0, -5.0, 13.0]

    """
    return parse.parse_kdist(self.run(f"KDIST,{kp1},{kp2}", **kwargs))

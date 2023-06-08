"""
pydita_ast
"""
# Copyright (c) 2023 ANSYS, Inc. All rights reserved.

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__.replace(".", "-"))
"""pydita_ast version."""

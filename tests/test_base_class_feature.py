# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
"""
Test script to demonstrate the base class inheritance feature.

This script tests the pattern-based base class configuration.
"""

from pyconverter.xml2py.utils.utils import get_base_class_for_pattern


def test_pattern_matching_with_rules(base_class_test_config):
    """Test various pattern matching scenarios with base class rules."""

    # Test cases
    test_cases = [
        ("apdl", "Abbreviations", "apdl/*", "APDLBase"),
        ("prep7", "Meshing", "prep7/Meshing", "PrepBase"),
        ("database", "Save", "*", "CommandsBase"),
        ("post1", "Analysis", "*", "CommandsBase"),
    ]

    for module_name, class_name, expected_pattern, expected_base_class in test_cases:
        result = get_base_class_for_pattern(base_class_test_config, module_name, class_name)

        assert result is not None, f"Expected result for {module_name}/{class_name}"
        assert (
            result["class_name"] == expected_base_class
        ), f"Expected {expected_base_class} for {module_name}/{class_name}, got {result['class_name']}"  # noqa: E501


def test_pattern_matching_without_rules(base_class_empty_config):
    """Test that no inheritance is applied when config has no base class rules."""

    test_cases = [
        ("apdl", "Abbreviations"),
        ("prep7", "Meshing"),
        ("database", "Save"),
        ("post1", "Analysis"),
    ]

    for module_name, class_name in test_cases:
        result = get_base_class_for_pattern(base_class_empty_config, module_name, class_name)

        assert (
            result is None
        ), f"Expected None for {module_name}/{class_name} when no rules defined, got {result}"


def test_specific_pattern_takes_precedence(base_class_test_config):
    """Test that more specific patterns are matched before wildcard patterns."""

    # prep7/Meshing should match the specific pattern, not the wildcard
    result = get_base_class_for_pattern(base_class_test_config, "prep7", "Meshing")

    assert result is not None
    assert result["class_name"] == "PrepBase"
    assert result["module"] == "ansys.mapdl.core._commands.prep"


def test_module_wildcard_pattern(base_class_test_config):
    """Test that module-level wildcard patterns work correctly."""

    # Any class in apdl module should get APDLBase
    result = get_base_class_for_pattern(base_class_test_config, "apdl", "SomeClass")

    assert result is not None
    assert result["class_name"] == "APDLBase"
    assert result["module"] == "ansys.mapdl.core._commands.apdl"


def test_global_wildcard_pattern(base_class_test_config):
    """Test that global wildcard pattern catches everything not matched."""

    # Random module/class should match the global wildcard
    result = get_base_class_for_pattern(base_class_test_config, "random", "RandomClass")

    assert result is not None
    assert result["class_name"] == "CommandsBase"
    assert result["module"] == "ansys.mapdl.core._commands"

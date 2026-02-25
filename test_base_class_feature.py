# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
"""
Test script to demonstrate the base class inheritance feature.

This script tests the pattern-based base class configuration.
"""
from pathlib import Path

from pyconverter.xml2py.utils.utils import get_base_class_for_pattern


def test_pattern_matching():
    """Test various pattern matching scenarios."""

    config_path = Path("config.yaml")

    print("Testing Base Class Pattern Matching")
    print("=" * 60)

    # Test cases
    test_cases = [
        ("apdl", "Abbreviations", "Should match 'apdl/*' pattern"),
        ("prep7", "Meshing", "Should match 'prep7/Meshing' pattern"),
        ("database", "Save", "Should not match if no pattern defined"),
        ("post1", "Analysis", "Should match '*' wildcard pattern"),
    ]

    for module_name, class_name, description in test_cases:
        result = get_base_class_for_pattern(config_path, module_name, class_name)

        print(f"\nTest: {module_name}/{class_name}")
        print(f"Description: {description}")

        if result:
            print(f"Inheritance: from {result['module']} import {result['class_name']}")
            print(f"Generated: class {class_name}({result['class_name']}):")
        else:
            print(f"No inheritance")
            print(f"Generated: class {class_name}:")

    print("\n" + "=" * 60)
    print("\nTo enable inheritance, uncomment rules in config.yaml:")
    print("1. Uncomment '- pattern: \"*\"' for all classes")
    print("2. Uncomment '- pattern: \"apdl/*\"' for specific module")
    print("3. Add custom patterns as needed")

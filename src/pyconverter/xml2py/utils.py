# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os

import pyconverter.xml2py.ast_tree as ast
import yaml


def parse_yaml(yaml_path):
    """
    Parse a YAML file.

    Parameters
    ----------

    yaml_path : str
        Path to the YAML file.
    """
    if os.path.isfile(yaml_path):
        with open(yaml_path, "r") as file:
            return yaml.safe_load(file)


def get_config_data_value(yaml_path, value):
    """
    Return the value of a specific key in the YAML file.

    Parameters
    ----------

    yaml_path : str
        Path to the YAML file.

    value : str
        Key to search for in the YAML file.
    """
    config_data = parse_yaml(yaml_path)
    return config_data.get(value)


def create_name_map(meta_command, yaml_file_path):
    # convert all to flat and determine number of occurances
    naive_names = []
    rules = get_config_data_value(yaml_file_path, "rules")
    specific_command_mapping = get_config_data_value(yaml_file_path, "specific_command_mapping")
    for ans_name in meta_command:
        ans_name = ans_name.lower()
        if not ans_name[0].isalnum():
            ans_name = ans_name[1:]
        naive_names.append(ans_name)

    # map command to pycommand function
    name_map = {}

    # second pass for each name
    for ans_name in meta_command:
        if ans_name in specific_command_mapping:
            py_name = specific_command_mapping[ans_name]
        else:
            lower_name = ans_name.lower()
            if not lower_name[0].isalnum():
                alpha_name = lower_name[1:]
            else:
                alpha_name = lower_name

            if naive_names.count(alpha_name) > 1:
                if rules:
                    py_name = lower_name
                    for rule_name, rule in rules.items():
                        py_name = py_name.replace(rule_name, rule)
                    if py_name == lower_name and not py_name[0].isalnum():
                        raise ValueError(
                            f"Additional rules need to be defined. The {ans_name} function name is in conflict with another function."  # noqa : E501
                        )
                else:
                    raise ValueError(
                        f"Function '{ans_name}' has identical name to another function."
                        "You need to provide RULES to differentiate them."
                    )

            else:
                py_name = alpha_name

        name_map[ans_name] = py_name

    ast.NameMap(name_map)

    return name_map


def import_handler(filename, additional_content, findalls):
    needed_imports = ""
    for match in findalls:
        needed_imports += f"{match[0]}\n"
        additional_content = additional_content.replace(match[0], "").replace("\n\n", "\n")

    with open(filename, "r+") as f:
        content = f.read()
        f.seek(0, 0)
        f.write(needed_imports + content + additional_content)


# ############################################################################
# AST functions
# ############################################################################


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

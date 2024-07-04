import yaml

RULES = {"/": "slash", "*": "star"}

def parse_package_structure(yaml_file_path):
    with open(yaml_file_path, "r") as yaml_file:
        data = yaml.safe_load(yaml_file)
    return data

def get_rules(yaml_file_path):
    data = parse_package_structure(yaml_file_path)
    print(data["rules"])
    return data["rules"]

def get_name_map(meta_command, yaml_file_path):
    # convert all to flat and determine number of occurances
    proc_names = []
    # get_rules(yaml_file_path) # This need to be modified, current format : [{'/': 'slash'}, {'*': 'star'}]
    for cmd_name in meta_command:
        cmd_name = cmd_name.lower()
        if not cmd_name[0].isalnum():
            cmd_name = cmd_name[1:]
        proc_names.append(cmd_name)

    # reserved command mapping
    COMMAND_MAPPING = {"*DEL": "stardel"}

    # map command to pycommand function
    name_map = {}

    # second pass for each name
    for ans_name in meta_command:
        if ans_name in COMMAND_MAPPING:
            py_name = COMMAND_MAPPING[ans_name]
        else:
            lower_name = ans_name.lower()
            if not lower_name[0].isalnum():
                alpha_name = lower_name[1:]
            else:
                alpha_name = lower_name

            if proc_names.count(alpha_name) != 1:
                if RULES: # need to get it from config file
                    py_name = lower_name
                    for rule_name, rule in RULES.items():
                        py_name = py_name.replace(rule_name, rule)
                    if py_name == lower_name and not py_name[0].isalnum():
                        raise ValueError(
                            f"Additional rules need to be defined. The {ans_name} function name is in conflict with another function."  # noqa : E501
                        )
                else:
                    raise ValueError(
                        "Some functions have identical names. You need to provide RULES."
                    )

            else:
                py_name = alpha_name

        name_map[ans_name] = py_name
    
    return name_map
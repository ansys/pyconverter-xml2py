import yaml

def parse_yaml(yaml_path):
    """
    Parse a YAML file.

    Parameters
    ----------

    yaml_path : str
        Path to the YAML file.
    """
    try:
        with open(yaml_path, "r") as file:
            yaml_data= yaml.safe_load(file)
    except FileNotFoundError:
        yaml_data = None
    return yaml_data

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
    try:
        output = config_data[value]
    except KeyError:
        output = None

    return output

def get_name_map(meta_command, yaml_file_path):
    # convert all to flat and determine number of occurances
    proc_names = []
    rules = get_config_data_value(yaml_file_path, "rules")
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
                if rules != None: # need to get it from config file
                    py_name = lower_name
                    for rule_name, rule in rules.items():
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
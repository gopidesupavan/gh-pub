# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "rich",
#     "pyyaml",
#     "jsonschema",
# ]
# ///
import json
import os

import yaml
from jsonschema.validators import validator_for
from rich.console import Console

console = Console(width=400, color_system="standard")

config_file = os.environ.get("RELEASE_CONFIG_FILE")
schema_path = os.environ.get("RELEASE_CONFIG_SCHEMA")

if not config_file:
    console.print(
        "[red]Error:  RELEASE_CONFIG_FILE not set[/]\n"
        "You must set `RELEASE_CONFIG_FILE` environment variable to run this script"
    )
    exit(1)


def set_outputs(yml_config):

    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        for root_element, root_values in yml_config.items():
            if isinstance(root_values, dict):
                for key, value in root_values.items():
                    f.write(f"{root_element}-{key}={json.dumps(value)}\n")
            else:
                f.write(f"{root_element}={json.dumps(root_values)}\n")


def read_file(path):
    if path.endswith(".yml") or path.endswith(".yaml"):
        with open(path) as file:
            return yaml.safe_load(file)

    if path.endswith(".json"):
        with open(path) as file:
            return json.load(file)


def validate_config(yml_config):
    exit_code = 0

    with open(schema_path) as schema_file:
        schema = json.loads(schema_file.read())

    validator = validator_for(schema)
    validator.check_schema(schema)

    for error in validator(schema).iter_errors(yml_config):
        exit_code = 1
        console.print(f"[red]Error: {error}[/]")

    if exit_code:
        console.print("[red]Release config validation failed[/]")


if __name__ == "__main__":
    yml_config_data = read_file(config_file)
    console.print("[blue]Release config validation started[/]")
    validate_config(yml_config_data)
    console.print("[blue]Release config validation passed[/]")
    console.print("[blue]Setting outputs[/]")
    set_outputs(yml_config_data)
    console.print("[blue]Outputs set[/]")

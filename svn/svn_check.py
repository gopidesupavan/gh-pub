# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "rich",
# ]
# ///
import json
import os
import re

from rich.console import Console

console = Console(width=400, color_system="standard")

svn_files = os.listdir()

unknown_files = []
unknown_file_extensions = []
valid_files = []
failed_count_check = []


def check_with_regex(file_to_check, pattern, check_type):
    match = re.match(pattern, file_to_check)

    if check_type == "extension":
        return match and file_to_check.endswith(match.group(1))

    elif check_type == "package_name":
        return match and match.group(1) in file_to_check


def check_files_with_identifiers(identifiers, all_files, check_type):
    all_files_copy = all_files.copy()

    for identifier in identifiers:
        if identifier.get("type") == "regex":
            regex_pattern = identifier.get("pattern")

            [
                all_files_copy.remove(file)
                for file in all_files
                if check_with_regex(file, regex_pattern, check_type)
            ]

    if check_type == "extension":
        unknown_file_extensions.extend(all_files_copy)

    elif check_type == "package_name":
        unknown_files.extend(all_files_copy)


if __name__ == "__main__":
    # con = [{"id": "extension", "description": "Validate svn package extensions", "identifiers": [{"type": "regex", "pattern": ".*(py3-none-any.whl|tar.gz.sha512|tar.gz.asc|tar.gz|py3-none-any.whl.asc|py3-none-any.whl.sha512)$"}]}, {"id": "package_name", "description": "Validate svn package names", "identifiers": [{"type": "regex", "pattern": ".*(apache_airflow.*)$"}, {"type": "regex", "pattern": ".*(apache-airflow.*)$"}]}]

    svn_check_config = json.loads(os.environ.get("SVN_CHECK_CONFIG"))

    for check in svn_check_config:
        console.print(f"[blue]{check.get('description')}[/]")
        check_files_with_identifiers(
            check.get("identifiers"), svn_files, check.get("id")
        )

    exit_code = 0

    if unknown_files:
        for error in unknown_files:
            console.print(f"[red]Error: unknown file found {error}[/]")
        exit_code = 1

    if unknown_file_extensions:
        for error in unknown_file_extensions:
            console.print(f"[red]Error: unknown file extension found {error}[/]")
        exit_code = 1

    if exit_code != 0:
        console.print("[red]SVN check failed[/]")
        exit(exit_code)

    console.print("[blue]SVN check passed successfully[/]")

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "rich",
# ]
# ///
from __future__ import annotations

import json
import os
import re
from typing import Any

from rich.console import Console

console = Console(width=400, color_system="standard")

svn_files = os.listdir()

unknown_files = []
unknown_file_extensions = []


def check_with_regex(file_to_check: str, pattern: str, check_type: str) -> bool | None:
    match = re.match(pattern, file_to_check)

    if check_type == "extension":
        return match and file_to_check.endswith(match.group(1))

    elif check_type == "package_name":
        return match and match.group(1) in file_to_check


def check_files_with_identifiers(
    identifiers: list[dict[str, Any]], all_files: list[str], check_type: str
):
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
    svn_check_config: list[dict[str, Any]] = json.loads(
        os.environ.get("SVN_CHECK_CONFIG")
    )

    if not svn_check_config:
        console.print(
            "[red]Error:  SVN_CHECK_CONFIG not set[/]\n"
            "You must set `SVN_CHECK_CONFIG` environment variable to run this script"
        )
        exit(1)

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

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "rich",
# ]
# ///

import json
import os
import re
import subprocess
import tempfile
from typing import Any
from rich.console import Console

console = Console(width=400, color_system="standard")

# Create a temporary directory to checkout the release folder files from svn
temp_svn_dist_release_dir = tempfile.TemporaryDirectory()

svn_files = os.listdir()

final_packages_to_publish = []


def is_extension_matched(file: str, pattern: str) -> bool:
    match = re.match(pattern, file)
    return match and file.endswith(match.group(1))


def checkout_release_files(compare_config):
    repo_url = compare_config.get("url")
    console.print(
        f"[blue]Checking out release files from {repo_url} to {temp_svn_dist_release_dir.name}[/]"
    )
    subprocess.run(["svn", "checkout", repo_url, temp_svn_dist_release_dir.name])


def extract_package_names(package_name_config: list[dict[str, Any]]):
    package_names: set[str] = set()
    for package_name_config in package_name_config:
        if package_name_config.get("type") == "regex":
            regex_pattern = package_name_config.get("pattern")
            package_names.update(
                match.group(1)
                for file in svn_files
                if (match := re.match(regex_pattern, file))
            )
    return list(package_names)


def find_matched_packages_between_dev_and_release(
    compare_config: dict[str, Any]
) -> list[str]:
    # This package names contains all the packages without rc or based on regex pattern extracted name
    dev_package_names = extract_package_names(compare_config.get("package_names"))
    if not dev_package_names:
        console.print(
            f"[red]No package names found to {os.environ.get('SOURCE_PATH')}[/]"
        )
        exit(1)

    release_folder_packages = os.listdir(path=temp_svn_dist_release_dir.name)
    matched_packages = [
        package
        for package in release_folder_packages
        if any(package.startswith(package_name) for package_name in dev_package_names)
    ]

    if not matched_packages:
        console.print(
            f"[red]No matched packages found between {os.environ.get('SOURCE_PATH')} and {temp_svn_dist_release_dir.name}[/]"
        )
        exit(1)
    return matched_packages


def exclude_packages_to_publish(
    packages: list[str], exclude_config: list[dict[str, Any]]
):
    exclude_packages: set[str] = set()
    for exclude_config in exclude_config:
        if exclude_config.get("type") == "regex":
            regex_pattern = exclude_config.get("pattern")
            [
                exclude_packages.add(package)
                for package in packages
                if is_extension_matched(package, regex_pattern)
            ]
    if exclude_packages:
        console.print(f"[blue]Following packages excluded: {exclude_packages}[/]")

    return list(set(packages) - exclude_packages)


def filter_rc_packages_to_publish(exclude_extensions_config: dict[str, Any]):
    svn_files_copy = svn_files.copy()
    print(svn_files_copy)
    packages_to_publish = exclude_packages_to_publish(
        svn_files_copy, exclude_extensions_config
    )
    final_packages_to_publish.extend(packages_to_publish)


def move_packages_to_dist_folder(packages_path: str):
    if not final_packages_to_publish:
        console.print("[red]No packages found to publish[/]")
        exit(1)

    for package_name in final_packages_to_publish:
        full_path = os.path.join(packages_path, package_name)
        subprocess.run(["mv", full_path, os.environ.get("DIST_PATH")])


def filter_pypi_version_packages_to_publish(compare_config, extension_exclude_config):
    # This package names contains all the packages without rc or based on regex pattern extracted name
    release_matched_packages = find_matched_packages_between_dev_and_release(
        compare_config
    )
    final_packages_to_publish.extend(
        exclude_packages_to_publish(release_matched_packages, extension_exclude_config)
    )
    # For PYPI_VERSION release we move the packages from the release folder to dist folder, only matched packages will be moved to dist folder
    move_packages_to_dist_folder(temp_svn_dist_release_dir.name)


if __name__ == "__main__":
    publish_config = json.loads(os.environ.get("PUBLISH_PACKAGES_CONFIG"))
    release_type = publish_config.get("release-type")
    extension_exclude_config = publish_config.get("exclude_extensions")

    if release_type == "RC_VERSION":
        filter_rc_packages_to_publish(extension_exclude_config)
        # For RC release we can directly move the packages from the provided source path
        move_packages_to_dist_folder(os.environ.get("SOURCE_PATH"))

    elif release_type == "PYPI_VERSION":
        compare_config = publish_config.get("compare")
        checkout_release_files(compare_config)
        filter_pypi_version_packages_to_publish(
            compare_config, extension_exclude_config
        )
    else:
        console.print(f"[red]Invalid release type {release_type}[/]")
        exit(1)

    console.print("[blue]Following packages will be published to PyPI[/]")
    for package in final_packages_to_publish:
        console.print(f"[blue]{package}[/]")

    console.print("[blue]To publish these packages to PyPI, set the mode=RELEASE[/]")

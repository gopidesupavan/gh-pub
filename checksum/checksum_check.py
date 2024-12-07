# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "rich",
# ]
# ///
import hashlib
import json
import os
from rich.console import Console

console = Console(width=400, color_system="standard")
svn_files = os.listdir()

invalid_checksums = []


def validate_checksum(check_sum_files: list[dict[str, str]], algorithm: str):
    for file_dict in check_sum_files:
        sha_file, check_file = file_dict.values()

        with open(check_file, "rb") as chk:
            digest = hashlib.file_digest(chk, algorithm)

        actual_sha = digest.hexdigest()

        with open(sha_file, "rb") as shf:
            content = shf.read().decode("utf-8").strip()

        expected_sha = content.split()[0]

        if actual_sha != expected_sha:
            invalid_checksums.append(
                {
                    "file": sha_file,
                    "expected_sha": expected_sha,
                    "actual_sha": actual_sha,
                }
            )


def get_valid_files(algorithm, files) -> list[dict[str, str]]:
    eligible_files = []
    for file in files:
        if file.endswith(algorithm):
            eligible_files.append(
                {
                    "sha_file": file,
                    "check_file": file.replace(algorithm, "").rstrip("."),
                }
            )
    return eligible_files


if __name__ == "__main__":
    # con = [{"id": "checksum", "description": "SHA512 Check", "algorithm": "sha512"}]
    check_sum_config = json.loads(os.environ.get("CHECK_SUM_CONFIG"))

    for check in check_sum_config:
        console.print(f"[blue]Checking {check.get('description')} checksum[/]")
        valid_files = get_valid_files(check.get("algorithm"), svn_files)
        validate_checksum(valid_files, check.get("algorithm"))

    if invalid_checksums:
        console.print("[red]Checksum validation failed[/]")
        for invalid in invalid_checksums:
            console.print(f"[red]File: {invalid.get('file')}[/]")
            console.print(f"[red]Expected SHA: {invalid.get('expected_sha')}[/]")
            console.print(f"[red]Actual SHA: {invalid.get('actual_sha')}[/]")
        exit(1)

    console.print("[blue]Checksum validation passed[/]")

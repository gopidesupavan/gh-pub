# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "rich",
#     "requests",
#     "python-gnupg",
# ]
# ///
import requests
from rich.console import Console

console = Console(width=400, color_system="standard")

import json
import os
import tempfile
import gnupg
svn_files = os.listdir()
temp_signature_key_file_path = tempfile.NamedTemporaryFile().name

invalid_signature_files = []

def download_keys(key_url):
    response = requests.get(key_url)
    if response.status_code != 200:
        console.print(f"[red]Error: Unable to download signature file from {key_url}: received: {response.status_code}[/]")
        exit(1)

    with open(temp_signature_key_file_path, "w") as key_file:
        key_file.write(response.text)

def validate_signature(signature_check):
    key_url = signature_check.get("keys")
    download_keys(key_url)
    gpg = gnupg.GPG()
    with open(temp_signature_key_file_path, "rb") as key_file:
        gpg.import_keys(key_file.read())

    for file in svn_files:
        if file.endswith(".asc"):
            with open(file, "rb") as singed_file:
                status = gpg.verify_file(fileobj_or_path=singed_file, data_filename=file.replace(".asc", ""))
            if not status.valid:
                invalid_signature_files.append({"file": file, "status": status.status})
            else:
                console.print(f"[blue]File {file} signed by {status.username}[/]")




if __name__ == "__main__":
    signature_check_config = json.loads(os.environ.get("SIGNATURE_CHECK_CONFIG"))

    for check in signature_check_config:
        console.print(f"[blue]Checking {check.get('description')} signature[/]")
        validate_signature(check)

    if invalid_signature_files:
        for error in invalid_signature_files:
            console.print(f"[red]Error: Invalid signature found for {error.get('file')} status: {error.get('status')}[/]")
        exit(1)

    console.print("[blue]All signatures are valid[/]")


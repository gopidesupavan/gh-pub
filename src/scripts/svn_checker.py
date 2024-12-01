import ast
import os
import re
import sys
from collections import Counter

unknown_files = []
unknown_file_extensions = []
valid_files = []
failed_count_check = []

def check_extension(file, extensions):
    for extension in extensions:
        if file.endswith(extension):
            print(f"File extension {extension} matched with {file}")
            return True
    return False

def extract_name(file_name_pattern, file):
    match = re.match(file_name_pattern, file)
    if match:
        name_before_version = match.group(1)
        return name_before_version
    return None

def validate_package_name_count(file_with_count, extensions):
    for package_name, count in file_with_count.items():
        if not (count == len(extensions)):
            failed_count_check.append(f"package name: {package_name}, count: {count}, expected count: {len(extensions)}")

def check_files(version_pattern: str, extensions: list[str]):
    exit_code = 0
    files = os.listdir()
    print(f"Found total files in {os.getcwd()}: ", len(files))
    for file in files:
        if not check_extension(file, extensions):
            unknown_file_extensions.append(file)
            continue

        package_name = extract_name(version_pattern, file)
        if not package_name:
            unknown_files.append(file)
            continue

        # Just to make sure that we are counting to same package name, ex: apache-airflow and apache_airflow in the dist folder
        valid_files.append(package_name.replace("-", "_"))

    file_with_count = Counter(valid_files)
    validate_package_name_count(file_with_count, extensions)

    if failed_count_check:
        print(f"Following packages are not matching the count: {failed_count_check}")
        exit_code = 1

    if unknown_files:
        exit_code = 1
        print(f"Following files are not matching the pattern: {unknown_files}")

    if unknown_file_extensions:
        exit_code = 1
        print(f"Following files are not matching the extensions: {unknown_file_extensions}")

    if exit_code == 0:
        print("SVN check passed successfully.")

    sys.exit(exit_code)



if __name__ == "__main__":
    file_extensions = ast.literal_eval(os.environ.get("FILE_EXTENSIONS"))
    version_format = os.environ.get("VERSION_FORMAT")
    check_files(version_format, file_extensions)
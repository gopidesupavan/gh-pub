import os
from unittest.mock import patch

from src.scripts.svn_checker import (check_extension, extract_name, validate_package_name_count,
                                     failed_count_check, check_files, unknown_files, unknown_file_extensions, valid_files)

def test_check_extension():

    assert check_extension("file.txt", [".txt"]) == True
    assert check_extension("file.txt", [".py"]) == False
    assert check_extension("file.py", [".py"]) == True
    assert check_extension("file.py", [".txt"]) == False

def test_extract_name():
    assert extract_name("^(.*?)-(rc\\d+-)?\\d+", "apache_airflow_client-2.10.0.tar.gz.sha512") == "apache_airflow_client"
    assert extract_name("^(.*?)-(rc\\d+-)?\\d+", "apache_airflow_providers_plexus-3.4.1.tar.gz") == "apache_airflow_providers_plexus"

def test_validate_package_name_count():

    validate_package_name_count({"apache_airflow": 2, "apache_airflow_providers_plexus": 2}, [".tar.gz", ".sha512"])
    assert failed_count_check == []

    validate_package_name_count({"apache_airflow": 1, "apache_airflow_providers_plexus": 2}, [".tar.gz", ".sha512"])
    assert len(failed_count_check) == 1

@patch('os.listdir')
def test_check_files(mock_listdir):
    unknown_files.clear()
    unknown_file_extensions.clear()
    valid_files.clear()
    failed_count_check.clear()

    mock_listdir.return_value = [
        'apache_airflow-2.10.0.tar.gz',
        'apache_airflow-2.10.0.tar.gz.sha512',
        'apache_airflow-2.10.0-py3-none-any.whl',
        'apache_airflow-2.10.0-py3-none-any.whl.sha512',
    ]

    os.environ['FILE_EXTENSIONS'] = "['.tar.gz', '.tar.gz.sha512', '-py3-none-any.whl', '-py3-none-any.whl.sha512']"
    os.environ['VERSION_FORMAT'] = '^(.*?)-(rc\\d+-)?\\d+'

    with patch('sys.exit') as mock_exit:
        check_files(os.environ['VERSION_FORMAT'], eval(os.environ['FILE_EXTENSIONS']))
        assert mock_exit.call_args[0][0] == 0


@patch('os.listdir')
def test_check_files_failed(mock_listdir):
    unknown_files.clear()
    unknown_file_extensions.clear()
    valid_files.clear()
    failed_count_check.clear()

    mock_listdir.return_value = [
        'apache_airflow-2.10.0.tar.gz',
        'apache_airflow-2.10.0.tar.gz.sha512',
        'apache_airflow-2.10.0-py3-none-any.whl',
        'apache_airflow-2.10.0-py3-none-any.whl.sha512',
        'dummy_file-2.10.0-py3-none-any.whl.sha512'
    ]

    os.environ['FILE_EXTENSIONS'] = "['.tar.gz', '.tar.gz.sha512', '-py3-none-any.whl', '-py3-none-any.whl.sha512']"
    os.environ['VERSION_FORMAT'] = '^(.*?)-(rc\\d+-)?\\d+'

    with patch('sys.exit') as mock_exit:
        check_files(os.environ['VERSION_FORMAT'], eval(os.environ['FILE_EXTENSIONS']))
        assert mock_exit.call_args[0][0] == 1

from unittest.mock import patch, mock_open
from checksum.checksum_check import get_valid_files, validate_checksum, invalid_checksums

class TestChecksumCheck:

    def test_get_valid_files(self):
        files = [
            'apache-airflow-2.10.3-source.tar.gz.sha512',
            'apache_airflow-2.10.3-py3-none-any.whl.asc',
            'apache_airflow-2.10.3-py3-none-any.whl.sha512',
            'apache_airflow-2.10.3.tar.gz'
        ]
        valida_files = get_valid_files('sha512', files)
        assert valida_files == [{'sha_file': 'apache-airflow-2.10.3-source.tar.gz.sha512', 'check_file': 'apache-airflow-2.10.3-source.tar.gz'}, {'sha_file': 'apache_airflow-2.10.3-py3-none-any.whl.sha512', 'check_file': 'apache_airflow-2.10.3-py3-none-any.whl'}]




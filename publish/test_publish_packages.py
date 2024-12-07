from unittest.mock import patch

import pytest
from publish.publish_packages import (
    exclude_packages_to_publish,
    filter_rc_packages_to_publish,
    final_packages_to_publish,
    svn_files,
    extract_package_names,
    find_matched_packages_between_dev_and_release,
)


class TestPublishPackages:

    @pytest.mark.parametrize(
        "packages, exclude_config, expected",
        [
            pytest.param(
                [
                    "airflow-provider-1.0.0.tar.gz.asc",
                    "package3-1.0.0.tar.gz",
                    "package2-1.0.0.py3-none-any.whl.sha512",
                    "package4-1.0.0.tar.gz",
                ],
                [
                    {
                        "type": "regex",
                        "pattern": r".*(tar.gz.asc|py3-none-any.whl.sha512)$",
                    },
                ],
                [
                    "package4-1.0.0.tar.gz",
                    "package3-1.0.0.tar.gz",
                ],
                id="exclude_few_package_extensions",
            ),
            pytest.param(
                [
                    "airflow-provider-1.0.0.tar.gz.asc",
                    "package2-1.0.0.py3-none-any.whl.sha512",
                ],
                [
                    {
                        "type": "regex",
                        "pattern": r".*(tar.gz.asc|py3-none-any.whl.sha512)$",
                    },
                ],
                [],
                id="exclude_all_given_packages",
            ),
        ],
    )
    def test_exclude_packages_to_publish(self, packages, exclude_config, expected):
        assert set(exclude_packages_to_publish(packages, exclude_config)) == set(
            expected
        )

    @pytest.mark.parametrize(
        "packages, exclude_config, expected",
        [
            pytest.param(
                [
                    "apache_airflow_providers_amazon-9.1.0rc1.tar.gz",
                    "apache_airflow_providers_amazon-9.1.0rc1.tar.gz.asc",
                    "apache_airflow_providers_amazon-9.1.0rc1.tar.gz.sha512",
                    "apache_airflow_providers_amazon-9.1.0rc1-py3-none-any.whl",
                    "apache_airflow_providers_amazon-9.1.0rc1-py3-none-any.whl.asc",
                    "apache_airflow_providers_amazon-9.1.0rc1-py3-none-any.whl.sha512",
                ],
                [
                    {
                        "type": "regex",
                        "pattern": r".*(.asc|.sha512)$",
                    },
                ],
                [
                    "apache_airflow_providers_amazon-9.1.0rc1-py3-none-any.whl",
                    "apache_airflow_providers_amazon-9.1.0rc1.tar.gz",
                ],
                id="return_rc_packages",
            ),
            pytest.param(
                [
                    "apache_airflow_providers_amazon-9.1.0rc1.tar.gz.asc",
                    "apache_airflow_providers_amazon-9.1.0rc1.tar.gz.sha512",
                ],
                [
                    {
                        "type": "regex",
                        "pattern": r".*(.asc|.sha512)$",
                    },
                ],
                [],
                id="no_rc_packages",
            ),
        ],
    )
    def test_filter_rc_packages_to_publish(self, packages, exclude_config, expected):
        svn_files.clear()
        svn_files.extend(packages)
        final_packages_to_publish.clear()
        filter_rc_packages_to_publish(exclude_config)
        assert set(final_packages_to_publish) == set(expected)

    @pytest.mark.parametrize(
        "packages, package_name_config, expected",
        [
            pytest.param(
                [
                    "apache_airflow_providers_amazon-9.1.0rc1.tar.gz",
                    "apache_airflow_providers_amazon-9.1.0rc1.tar.gz.asc",
                    "apache_airflow_providers_amazon-9.1.0rc1.tar.gz.sha512",
                    "apache_airflow_providers_amazon-9.1.0rc1-py3-none-any.whl",
                    "apache_airflow_providers_amazon-9.1.0rc1-py3-none-any.whl.asc",
                    "apache_airflow_providers_amazon-9.1.0rc1-py3-none-any.whl.sha512",
                    "apache_airflow_providers_airbyte-10.1.0rc1.tar.gz",
                    "apache_airflow_providers_airbyte-10.1.0rc1.tar.gz.asc",
                    "apache_airflow_providers_airbyte-10.1.0rc1.tar.gz.sha512",
                    "apache_airflow_providers_airbyte-10.1.0rc1-py3-none-any.whl",
                    "apache_airflow_providers_airbyte-10.1.0rc1-py3-none-any.whl.asc",
                    "apache_airflow_providers_airbyte-10.1.0rc1-py3-none-any.whl.sha512",
                ],
                [
                    {
                        "type": "regex",
                        "pattern": "(apache_airflow_providers.*?)(?=rc)",
                    },
                ],
                [
                    "apache_airflow_providers_amazon-9.1.0",
                    "apache_airflow_providers_airbyte-10.1.0",
                ],
                id="return_package_name_without_rc",
            ),
        ],
    )
    def test_extract_package_names(self, packages, package_name_config, expected):
        svn_files.clear()
        svn_files.extend(packages)
        extracted_names = extract_package_names(package_name_config)
        assert set(extracted_names) == set(expected)

    @pytest.mark.parametrize(
        "compare_config, temp_release_dir_files, temp_svn_files, expected",
        [
            pytest.param(
                {
                    "url": "https://dist.apache.org/repos/dist/release/airflow/",
                    "path": "airflow/providers/",
                    "package_names": [
                        {
                            "type": "regex",
                            "pattern": "(apache_airflow_providers.*?)(?=rc)",
                        }
                    ],
                },
                [
                    "apache_airflow_providers_amazon-9.1.0.tar.gz",
                    "apache_airflow_providers_amazon-9.1.0.tar.gz.asc",
                    "apache_airflow_providers_amazon-9.1.0.tar.gz.sha512",
                    "apache_airflow_providers_amazon-9.1.0-py3-none-any.whl",
                    "apache_airflow_providers_amazon-9.1.0-py3-none-any.whl.asc",
                    "apache_airflow_providers_amazon-9.1.0-py3-none-any.whl.sha512",
                    "apache_airflow_providers_airbyte-10.1.0.tar.gz",
                    "apache_airflow_providers_airbyte-10.1.0.tar.gz.asc",
                    "apache_airflow_providers_airbyte-10.1.0.tar.gz.sha512",
                    "apache_airflow_providers_airbyte-10.1.0-py3-none-any.whl",
                    "apache_airflow_providers_airbyte-10.1.0-py3-none-any.whl.asc",
                    "apache_airflow_providers_airbyte-10.1.0-py3-none-any.whl.sha512",
                ],
                [
                    "apache_airflow_providers_amazon-9.1.0rc1.tar.gz",
                    "apache_airflow_providers_amazon-9.1.0rc1.tar.gz.asc",
                    "apache_airflow_providers_amazon-9.1.0rc1.tar.gz.sha512",
                    "apache_airflow_providers_amazon-9.1.0rc1-py3-none-any.whl",
                    "apache_airflow_providers_amazon-9.1.0rc1-py3-none-any.whl.asc",
                    "apache_airflow_providers_amazon-9.1.0rc1-py3-none-any.whl.sha512",
                    "apache_airflow_providers_airbyte-10.1.0rc1.tar.gz",
                    "apache_airflow_providers_airbyte-10.1.0rc1.tar.gz.asc",
                    "apache_airflow_providers_airbyte-10.1.0rc1.tar.gz.sha512",
                    "apache_airflow_providers_airbyte-10.1.0rc1-py3-none-any.whl",
                    "apache_airflow_providers_airbyte-10.1.0rc1-py3-none-any.whl.asc",
                    "apache_airflow_providers_airbyte-10.1.0rc1-py3-none-any.whl.sha512",
                ],
                [
                    "apache_airflow_providers_amazon-9.1.0.tar.gz",
                    "apache_airflow_providers_amazon-9.1.0.tar.gz.asc",
                    "apache_airflow_providers_amazon-9.1.0.tar.gz.sha512",
                    "apache_airflow_providers_amazon-9.1.0-py3-none-any.whl",
                    "apache_airflow_providers_amazon-9.1.0-py3-none-any.whl.asc",
                    "apache_airflow_providers_amazon-9.1.0-py3-none-any.whl.sha512",
                    "apache_airflow_providers_airbyte-10.1.0.tar.gz",
                    "apache_airflow_providers_airbyte-10.1.0.tar.gz.asc",
                    "apache_airflow_providers_airbyte-10.1.0.tar.gz.sha512",
                    "apache_airflow_providers_airbyte-10.1.0-py3-none-any.whl",
                    "apache_airflow_providers_airbyte-10.1.0-py3-none-any.whl.asc",
                    "apache_airflow_providers_airbyte-10.1.0-py3-none-any.whl.sha512",
                ],
                id="find_matched_packages_between_dev_and_release",
            ),
            pytest.param(
                {
                    "url": "https://dist.apache.org/repos/dist/release/airflow/",
                    "path": "airflow/providers/",
                    "package_names": [
                        {
                            "type": "regex",
                            "pattern": "(apache_airflow_providers.*?)(?=rc)",
                        }
                    ],
                },
                [
                    "apache_airflow_providers_amazon-9.1.0.tar.gz",
                    "apache_airflow_providers_amazon-9.1.0.tar.gz.asc",
                    "apache_airflow_providers_amazon-9.1.0.tar.gz.sha512",
                    "apache_airflow_providers_amazon-9.1.0-py3-none-any.whl",
                    "apache_airflow_providers_amazon-9.1.0-py3-none-any.whl.asc",
                    "apache_airflow_providers_amazon-9.1.0-py3-none-any.whl.sha512",
                    "apache_airflow_providers_airbyte-10.1.0.tar.gz",
                    "apache_airflow_providers_airbyte-10.1.0.tar.gz.asc",
                    "apache_airflow_providers_airbyte-10.1.0.tar.gz.sha512",
                    "apache_airflow_providers_airbyte-10.1.0-py3-none-any.whl",
                    "apache_airflow_providers_airbyte-10.1.0-py3-none-any.whl.asc",
                    "apache_airflow_providers_airbyte-10.1.0-py3-none-any.whl.sha512",
                ],
                [
                    "apache_airflow_providers_amazon-9.1.0rc1.tar.gz",
                    "apache_airflow_providers_amazon-9.1.0rc1.tar.gz.asc",
                    "apache_airflow_providers_amazon-9.1.0rc1.tar.gz.sha512",
                    "apache_airflow_providers_amazon-9.1.0rc1-py3-none-any.whl",
                    "apache_airflow_providers_amazon-9.1.0rc1-py3-none-any.whl.asc",
                    "apache_airflow_providers_amazon-9.1.0rc1-py3-none-any.whl.sha512",
                ],
                [
                    "apache_airflow_providers_amazon-9.1.0.tar.gz",
                    "apache_airflow_providers_amazon-9.1.0.tar.gz.asc",
                    "apache_airflow_providers_amazon-9.1.0.tar.gz.sha512",
                    "apache_airflow_providers_amazon-9.1.0-py3-none-any.whl",
                    "apache_airflow_providers_amazon-9.1.0-py3-none-any.whl.asc",
                    "apache_airflow_providers_amazon-9.1.0-py3-none-any.whl.sha512",
                ],
                id="find_matched_packages_between_dev_and_release_should_return_one_provider",
            ),
        ],
    )
    @patch("publish.publish_packages.os.listdir")
    def test_find_matched_packages_between_dev_and_release(
        self,
        mock_listdir,
        compare_config,
        temp_release_dir_files,
        temp_svn_files,
        expected,
    ):
        mock_listdir.return_value = temp_release_dir_files
        svn_files.clear()
        svn_files.extend(temp_svn_files)
        matched_package_names = find_matched_packages_between_dev_and_release(
            compare_config
        )
        assert set(matched_package_names) == set(expected)

    @patch("publish.publish_packages.os.listdir")
    def test_find_matched_packages_between_dev_and_release_when_no_match_should_fail(
        self,
        mock_listdir,
    ):
        mock_listdir.return_value = [
            "apache_airflow_providers_amazon-9.1.0.tar.gz",
            "apache_airflow_providers_amazon-9.1.0.tar.gz.asc",
            "apache_airflow_providers_amazon-9.1.0.tar.gz.sha512",
        ]
        svn_files.clear()
        svn_files.extend(
            [
                "apache_airflow_providers_airbyte-10.1.0.tar.gz.sha512",
            ]
        )

        with pytest.raises(SystemExit):
            find_matched_packages_between_dev_and_release(
                {
                    "url": "https://dist.apache.org/repos/dist/release/airflow/",
                    "path": "airflow/providers/",
                    "package_names": [
                        {
                            "type": "regex",
                            "pattern": "(apache_airflow_providers.*?)(?=rc)",
                        }
                    ],
                }
            )

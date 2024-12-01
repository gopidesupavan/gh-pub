# Gh Publish

## Description
`Gh Publish` is a GitHub Action designed to validate artifacts and publish to PyPI. It includes steps for setting up Python, parsing configuration files, checking out SVN repositories, performing SVN and checksum checks, and publishing to PyPI.

## Inputs
- `publish-config` (required): Path to the publish config file. Default is `publish-config.yml`.
- `temp-dir` (optional): Temporary directory to checkout SVN repo. Default is `temp-svn-repo`.
- `mode` (optional): Mode to run the action. Default is `verify`.

## Usage
To use this action, include it in your workflow YAML file:

```yaml
name: Publish to PyPI

on:
  workflow_dispatch:


jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Gh Publish
        uses: ./gopidesupavan/gh-pub@main
        with:
          publish-config: 'path/to/your/publish-config.yml'
          temp-dir: 'temp-svn-repo'
          mode: 'publish'
```
# About publish-config.yml

The `publish-config.yml` file has composed of multiple rules to validate the artifacts and publish them to PyPI. The configuration file is structured as follows:

```yaml
project:
    Name: example-pub
    Description: Example project for publishing to PyPI

publishers:
    name: providers
    url: https://dist.apache.org/repos/dist/dev/airflow/
    path: "airflow/providers/pypi"
    version_pattern: '^(.*?)-(rc\d+-)?\d+'
    extensions:
      - .tar.gz
      - .tar.gz.asc
      - .tar.gz.sha512
      - -py3-none-any.whl
      - -py3-none-any.whl.asc
      - -py3-none-any.whl.sha512
    rules:
      svn-check:
          name: "SVN Check"
          type: "svn"
          enabled: "false"
      checksum-check:
          name: "SHA512 Check"
          type: "512"
          enabled: "true"
          script: "/home/runner/work/example-pub/example-pub/scripts/checksum_check.sh"
```
svn-check: This rule is used to validate the package extension. It checks each package have the required extension or not. eg: .tar.gz, .tar.gz.asc, .tar.gz.sha512, -py3-none-any.whl, -py3-none-any.whl.asc, -py3-none-any.whl.sha512, total 6 extensions are required. 

checksum-check: This rule is used to validate the checksum of the package. It checks the checksum of the package with the provided checksum type. eg: SHA512 checksum is required for each package.

script: Script use to validate the rules. if there is no script provided in the publish-config.yml file, the default script will be used to validate the rules. default scripts are under the src/scripts directory.
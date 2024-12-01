import os
import sys
import json
import yaml

DEFAULT_SVN_CHECKER_SCRIPT = "{github_action_path}/src/scripts/svn_checker.py"
DEFAULT_CHECK_SUM_SCRIPT = "{github_action_path}/src/scripts/checksum_check.sh"


def set_default_config(config_data):
    svn_checker_script = config_data.get("publishers", {}).get("rules", {}).get("svn-check", {}).get("script")
    if not svn_checker_script:
        config_data["publishers"]["rules"]["svn-check"]["script"] = DEFAULT_SVN_CHECKER_SCRIPT.format(github_action_path=os.environ.get("GITHUB_ACTION_PATH"))

    check_sum_script = config_data.get("publishers", {}).get("rules", {}).get("checksum-check", {}).get("script")
    if not check_sum_script:
        config_data["publishers"]["rules"]["checksum-check"]["script"] = DEFAULT_CHECK_SUM_SCRIPT.format(github_action_path=os.environ.get("GITHUB_ACTION_PATH"))

    return config_data


def parse_config(path):
    with open(path, 'r') as file:
        config_data = yaml.safe_load(file)

    updated_config_data = set_default_config(config_data)

    def set_multiline_output(name, updated_data):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            value = json.dumps(updated_data)
            fh.write(f'{name}={value}')
            
    set_multiline_output("pub_config", updated_config_data)



if __name__ == '__main__':
    config_path = sys.argv[1]
    parse_config(config_path)

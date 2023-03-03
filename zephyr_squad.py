import argparse
import json
from colorama import Fore
from support.zephyr_api import get_cycle_by_name, get_folder_by_name, load_jira_project_settings, load_variables, populate_tests_to_folders, update_tests, update_tests_by_keys
from support.utils import get_test_results


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--command', '-m',
        help='Choose a command to execute',
        type=str,
        choices=["populate", "publish", "publish-static"],
        required=True
    )

    parser.add_argument('--config_file', nargs='+',
                        help='Config file with folders and filters to populate a cycle')

    parser.add_argument('--test_result_file', nargs='+',
                        help='Test result file with status of the tests')

    parser.add_argument('--version_name', nargs='+',
                        help='Name of the Release Version')

    args = parser.parse_args()
    options(args)
    load_variables(args.config_file[0])
    load_jira_project_settings(args.version_name[0])
    if args.command == "populate":
        populate_tests_to_folders()

    if args.command == "publish":
        options_publish(args)
        test_results = get_test_results(args.test_result_file[0])
        cycle_id = get_cycle_by_name()
        folder_ids = get_folder_by_name(cycle_id)
        if (not folder_ids):
            print(Fore.YELLOW + '¬ No Automated Folder was specficied.' + Fore.WHITE)
            exit(0)
        update_tests(cycle_id, folder_ids, test_results)

    if args.command == "publish-static":
        config_file = open("zephyr_keys_status.json")
        ZEPHYR_KEYS_STATUS = json.load(config_file)
        test_results = ZEPHYR_KEYS_STATUS["keys"]
        status = ZEPHYR_KEYS_STATUS["status"]
        cycle_id = get_cycle_by_name()
        folder_ids = get_folder_by_name(cycle_id)
        if (not folder_ids):
            print(Fore.YELLOW + '¬ No Automated Folder was specficied.' + Fore.WHITE)
            exit(0)
        update_tests_by_keys(cycle_id, folder_ids, test_results, status)


def options(args):
    if args.config_file is None:
        print("[Missing --config_file param] - You need to pass a path to config file")
        exit(0)
    if args.version_name is None:
        print("[Missing --version_name param] - You need to pass a release version name")
        exit(0)


def options_publish(args):
    if args.test_result_file is None:
        print(
            "[Missing --test_result_file param] - You need to pass a path to test result file")
        exit(0)


if __name__ == "__main__":
    main()


import json
import re
from support.TestStatus import TestStatus

PATTERN = r'@(.*?) '


def convert_status_to_enum(status):
    switcher = {
        "passed": TestStatus.PASS,
        "failed": TestStatus.FAIL,
        "pending": TestStatus.WIP,
        "blocked": TestStatus.BLOCKED,
    }
    return switcher.get(status, "Invalid Status")


def get_test_results(test_result_file):
    test_file = open(test_result_file)
    results = json.load(test_file)
    result_lits = []
    for res in results["results"]:
        for suite in res["suites"]:
            for test in suite["tests"]:
                testKey = re.search(PATTERN, test["title"]).group(1)
                result_lits.append(
                    (testKey, convert_status_to_enum(test["state"])))
    return result_lits

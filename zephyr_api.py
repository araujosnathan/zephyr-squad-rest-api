import json
import re
import jwt
import time
import hashlib
import requests
import os
from colorama import Fore
from TestStatus import TestStatus

# Get environment variables
USER = ""
ACCESS_KEY = ""
SECRET_KEY = ""
USER_ENV = os.getenv('ZEPHYR_USER')
ACCESS_KEY_ENV = os.getenv('ZEPHYR_ACCESS_KEY')
SECRET_KEY_ENV = os.getenv('ZEPHYR_SECRET_KEY')
JWT_EXPIRE = 3600
ZEPHYR_CONFIG = None

# '../zephyr_config_local.json'


def load_variables(config_file):
    global ZEPHYR_CONFIG
    config_file = open(config_file)
    ZEPHYR_CONFIG = json.load(config_file)
    global USER, ACCESS_KEY, SECRET_KEY
    if("user" in ZEPHYR_CONFIG and ZEPHYR_CONFIG["user"] is not None and ZEPHYR_CONFIG["user"] != ""):
        USER = ZEPHYR_CONFIG["user"]
    else:
        USER = USER_ENV
        if(USER is None):
            raise Exception(Fore.RED + "\nø User is required\n" + Fore.WHITE)

    if("acccess_key" in ZEPHYR_CONFIG and ZEPHYR_CONFIG["acccess_key"] is not None and ZEPHYR_CONFIG["acccess_key"] != ""):
        ACCESS_KEY = ZEPHYR_CONFIG["acccess_key"]
    else:
        ACCESS_KEY = ACCESS_KEY_ENV
        if(ACCESS_KEY is None):
            raise Exception(
                Fore.RED + "\nø Access Key is required\n" + Fore.WHITE)

    if("secret_key" in ZEPHYR_CONFIG and ZEPHYR_CONFIG["secret_key"] is not None and ZEPHYR_CONFIG["secret_key"] != ""):
        SECRET_KEY = ZEPHYR_CONFIG["secret_key"]
    else:
        SECRET_KEY = SECRET_KEY_ENV
        if(SECRET_KEY is None):
            raise Exception(
                Fore.RED + "\nø Secret Key is required\n" + Fore.WHITE)


def get_jwt_token(canonical_path):
    payload_token = {
        'sub': USER,
        'qsh': hashlib.sha256(canonical_path.encode('utf-8')).hexdigest(),
        'iss': ACCESS_KEY,
        'exp': int(time.time())+JWT_EXPIRE,
        'iat': int(time.time())
    }
    response = jwt.encode(payload_token, SECRET_KEY,
                          algorithm='HS256').strip()
    if(response is not None):
        return response
    else:
        raise Exception(Fore.RED + "\nø Token not generated\n" + Fore.WHITE)


def build_headers(jwt_token, content_type):
    return {
        'Authorization': 'JWT '+jwt_token,
        'zapiAccessKey': ACCESS_KEY,
        'Content-Type': content_type
    }


def get_cycles():
    path = '/public/rest/api/1.0/cycles/search'
    RELATIVE_PATH = path + "?versionId={}&projectId={}".format(
        ZEPHYR_CONFIG["version_id"], ZEPHYR_CONFIG["project_id"])
    CANONICAL_PATH = 'GET&' + path + "&projectId={}&versionId={}".format(
        ZEPHYR_CONFIG["project_id"], ZEPHYR_CONFIG["version_id"])
    jwt_token = get_jwt_token(CANONICAL_PATH)
    headers = build_headers(jwt_token, 'text/plain')

    response = requests.get(
        ZEPHYR_CONFIG["base_url"] + RELATIVE_PATH, headers=headers)

    if(response.status_code == 200):
        jsonResponse = response.json()
        return jsonResponse
    else:
        raise Exception(
            Fore.RED + "\nø It was not possible to get Cycles" + Fore.WHITE)


def get_cycle_by_name():
    existing_cycles = get_cycles()
    retrieved_cycle = list(
        filter(lambda cycle: cycle.get('name') == ZEPHYR_CONFIG["cycle_name"], existing_cycles))
    if(retrieved_cycle):
        return retrieved_cycle[0].get('id')
    else:
        return None


def get_folder_by_name(cycle_id):
    folders = []
    existing_folders = get_folders(cycle_id)
    for folder in ZEPHYR_CONFIG["folders"]:
        if(folder['type'] == "Auto"):
            retrieved_folder = list(
                filter(lambda folder: folder.get('name') == folder['name'], existing_folders))
            if(retrieved_folder):
                folders.append(retrieved_folder[0].get('id'))
    return folders


def get_test_by_key(array_tests, test_key):
    retrieved_test = list(
        filter(lambda test: test.get('issueKey') == test_key, array_tests))
    if(retrieved_test):
        return retrieved_test[0].get('execution').get('id'), retrieved_test[0].get('execution').get('issueId')
    else:
        return None, None


def get_folders(cycle_id):
    path = '/public/rest/api/1.0/folders'
    RELATIVE_PATH = path + "?versionId={}&cycleId={}&projectId={}".format(
        ZEPHYR_CONFIG["version_id"], cycle_id, ZEPHYR_CONFIG["project_id"])
    CANONICAL_PATH = 'GET&' + path + "&cycleId={}&projectId={}&versionId={}".format(
        cycle_id, ZEPHYR_CONFIG["project_id"], ZEPHYR_CONFIG["version_id"])
    jwt_token = get_jwt_token(CANONICAL_PATH)
    headers = build_headers(jwt_token, 'text/plain')

    response = requests.get(
        ZEPHYR_CONFIG["base_url"] + RELATIVE_PATH, headers=headers)
    if(response.status_code == 200):
        jsonResponse = response.json()
        return jsonResponse
    else:
        raise Exception(
            Fore.RED + "ø It was not possible to get Folders" + Fore.WHITE)


def create_cycle():
    path = '/public/rest/api/1.0/cycle'
    RELATIVE_PATH = path
    CANONICAL_PATH = 'POST&' + path + '&'
    jwt_token = get_jwt_token(CANONICAL_PATH)
    headers = build_headers(jwt_token, 'application/json')

    payload_new_cycle = {"name": ZEPHYR_CONFIG["cycle_name"],
                         "versionId": ZEPHYR_CONFIG["version_id"], "projectId": ZEPHYR_CONFIG["project_id"]}

    existing_cycles = get_cycles()
    retrieved_cycle = list(
        filter(lambda cycle: cycle.get('name') == ZEPHYR_CONFIG["cycle_name"], existing_cycles))
    if(retrieved_cycle):
        print(Fore.YELLOW + '¬ Cycle {} already existing. Using it.'.format(
            ZEPHYR_CONFIG["cycle_name"]) + Fore.WHITE)
        return retrieved_cycle[0].get('id')
    else:
        response = requests.post(
            ZEPHYR_CONFIG["base_url"] + RELATIVE_PATH, headers=headers, json=payload_new_cycle)
        jsonResponse = response.json()
        try:
            CYCLEID = jsonResponse['id']
            print(Fore.GREEN + '√ Cycle {} created with success.'.format(
                ZEPHYR_CONFIG["cycle_name"]) + Fore.WHITE)
            return CYCLEID
        except:
            raise Exception(
                Fore.RED + "ø It was not possible to create Cycle." + Fore.WHITE)


def create_folder(cycle_id, folder_name):
    path = '/public/rest/api/1.0/folder'
    RELATIVE_PATH = path
    CANONICAL_PATH = 'POST&' + path + '&'
    jwt_token = get_jwt_token(CANONICAL_PATH)
    headers = build_headers(jwt_token, 'application/json')

    payloadFolder = {"name": folder_name,
                     "cycleId": cycle_id, "versionId": ZEPHYR_CONFIG["version_id"], "projectId": ZEPHYR_CONFIG["project_id"]}

    response = requests.post(
        ZEPHYR_CONFIG["base_url"] + RELATIVE_PATH, headers=headers, json=payloadFolder)

    jsonResponse = response.json()
    if(response.status_code == 400 and jsonResponse['errorCode'] == 152):
        existing_folders = get_folders(cycle_id)
        retrieved_folder = list(
            filter(lambda folder: folder.get('name') == folder_name, existing_folders))
        if(retrieved_folder):
            print(
                Fore.YELLOW + '¬ Folder {} already existing. Using it.'.format(folder_name) + Fore.WHITE)
            return retrieved_folder[0].get('id')
    else:
        try:
            FOLDERID = jsonResponse['id']
            print(
                Fore.GREEN + '√ Folder created with success: {}.'.format(folder_name) + Fore.WHITE)
            return FOLDERID
        except:
            raise Exception(
                Fore.RED + "ø It was not possible to create Folder: {}".format(folder_name) + Fore.WHITE)


def add_tests_to_folder(cycle_id, folder_id, filter_query):
    path = "/public/rest/api/1.0/executions/add/folder/"
    RELATIVE_PATH = path + '{}'.format(folder_id)
    CANONICAL_PATH = 'POST&' + path + str(folder_id)+"&"

    jwt_token = get_jwt_token(CANONICAL_PATH)
    headers = build_headers(jwt_token, 'application/json')

    query = filter_query
    payload_add_tests = {"jql": query, "method": 2, "versionId": ZEPHYR_CONFIG["version_id"],
                         "projectId": ZEPHYR_CONFIG["project_id"], "cycleId": cycle_id}

    response = requests.post(
        ZEPHYR_CONFIG["base_url"] + RELATIVE_PATH, headers=headers, json=payload_add_tests)
    if(response.status_code == 200):
        print(Fore.GREEN + '√ Tests added with success to previous folder.\n' + Fore.WHITE)
    else:
        raise Exception(
            Fore.RED + "ø It was not possible to add tetes to folder ... Status Code: {}\n".format(response.status_code) + Fore.WHITE)


def populate_tests_to_folders():
    cycle_id = create_cycle()
    folders = ZEPHYR_CONFIG["folders"]
    for folder in folders:
        folder_id = create_folder(cycle_id, folder["name"])
        add_tests_to_folder(cycle_id, folder_id, folder["query"])
        print()


def update_execution(cycle_id, test_key, execution_id, issue_id, status):
    path = '/public/rest/api/1.0/execution/{}'.format(execution_id)
    RELATIVE_PATH = path

    CANONICAL_PATH = 'PUT&' + path + "&"
    jwt_token = get_jwt_token(CANONICAL_PATH)
    headers = build_headers(jwt_token, 'application/json')

    payload_update = {"status": {"id": status},
                      "projectId": ZEPHYR_CONFIG['project_id'], "issueId": issue_id, "cycleId": cycle_id, "versionId": ZEPHYR_CONFIG['version_id']}

    response = requests.put(
        ZEPHYR_CONFIG["base_url"] + RELATIVE_PATH, headers=headers, json=payload_update)
    if(response.status_code == 200):
        print(Fore.GREEN + '√ Test {} updated with success.'.format(test_key) + Fore.WHITE)
    else:
        raise Exception(
            Fore.RED + "ø It was not possible to update the Test {}".format(test_key) + Fore.WHITE)


def get_tests_from_folder(cycle_id, folder_id):
    path = '/public/rest/api/1.0/executions/search/folder/{}'.format(folder_id)
    RELATIVE_PATH = path + "?versionId={}&cycleId={}&projectId={}".format(
        ZEPHYR_CONFIG["version_id"], cycle_id, ZEPHYR_CONFIG["project_id"])

    CANONICAL_PATH = 'GET&' + path + "&cycleId={}&projectId={}&versionId={}".format(
        cycle_id, ZEPHYR_CONFIG["project_id"], ZEPHYR_CONFIG["version_id"])
    jwt_token = get_jwt_token(CANONICAL_PATH)
    headers = build_headers(jwt_token, 'text/plain')

    response = requests.get(
        ZEPHYR_CONFIG["base_url"] + RELATIVE_PATH, headers=headers)
    if(response.status_code == 200):
        jsonResponse = response.json()
        return jsonResponse["searchObjectList"]
    else:
        raise Exception(
            Fore.RED + "ø It was not possible to get tests from specific." + Fore.WHITE)


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
                testKey = re.search('@ER-(.*?) ', test["title"]).group(1)
                result_lits.append(
                    ("ER-{}".format(testKey), convert_status_to_enum(test["state"])))
    return result_lits


def update_tests(cycle_id, folder_ids, test_results):
    for folder_id in folder_ids:
        tests_from_folder = get_tests_from_folder(cycle_id, folder_id)
        for key, status in test_results:
            execution_id, issue_id = get_test_by_key(
                tests_from_folder, key)
            if(issue_id):
                update_execution(cycle_id, key, execution_id,
                                 issue_id, status)

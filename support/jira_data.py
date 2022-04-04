from jira import JIRA

MYJIRA = None


def jira_auth(base_url, user, api_token):
    global MYJIRA
    options = {'server': base_url}
    MYJIRA = JIRA(options, basic_auth=(user, api_token))


def get_projet_id(project_key):
    return MYJIRA.project(project_key).id


def get_version_id(project_key, version_name):
    versions = MYJIRA.project_versions(project_key)
    version_retrived = list(
        filter(lambda version: version.name == version_name, versions))
    return version_retrived[0].id


def get_test_issues_by_filter(filter_id):
    test_issues_list = []
    start = 0
    max = 100
    while MYJIRA.search_issues('filter={}'.format(filter_id), startAt=start, maxResults=max):
        for issue in MYJIRA.search_issues('filter={}'.format(filter_id), startAt=start, maxResults=max):
            test_issues_list.append(issue.key)
        start = start + 100
    return test_issues_list

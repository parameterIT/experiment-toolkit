import requests
import time

from math import ceil
from typing import List

_BASE_CODE_CLIMATE_URL = "https://api.codeclimate.com/v1/"
_PAGE_SIZE: int = 100

class Build:
    def __init__(self, id: str, repo_id: str, number: int, state: str):
        self.id = id
        self.repo_id = repo_id
        self.number = number
        self.state = state


class Snapshot:
    def __init__(self, id: str, repo_id: str, issue_count: int):
        self.id = id
        self.issue_count = issue_count
        self.repo_id = repo_id
        self.pages = ceil(issue_count / _PAGE_SIZE)


class Issue:
    def __init__(self, metric: str, aggregates_into: str):
        self.metric = metric
        self.aggregates_into = aggregates_into


class Client:
    def __init__(self, api_token: str):
        self.api_token = api_token

    def get_id_for_repo(self, github_slug: str) -> str:
        """
        Returns the id associated with the given github_slug on code climate, assuming
        that the github_slug exists for the account associated with the api token
        """
        target = f"{_BASE_CODE_CLIMATE_URL}repos?github_slug={github_slug}"
        headers = {"Authorization": f"Token token={self.api_token}"}

        resp = requests.get(target, headers=headers)
        json_resp = resp.json()
        repo_id = json_resp["data"][0]["id"]

        return repo_id

    def get_latest_build_for(self, repo_id: str) -> Build:
        """
        Returns the latest build for the given repo id, assuming that the first build
        on the first page corresponds to the latest build number.

        The build number should be the maximum of all build numbers
        """
        target = f"{_BASE_CODE_CLIMATE_URL}repos/{repo_id}/builds?page[number]=1&page[size]=1"
        headers = {"Authorization": f"Token token={self.api_token}"}

        resp = requests.get(target, headers=headers)
        json_resp = resp.json()

        id = json_resp["data"][0]["id"]
        number = json_resp["data"][0]["attributes"]["number"]
        state = json_resp["data"][0]["attributes"]["state"]

        return Build(id, repo_id, number, state)

    def get_build(self, number: int, repo_id: str) -> Build:
        """
        Return the build of the specific build number, assuming that the build number exists.
        """
        target = f"{_BASE_CODE_CLIMATE_URL}repos/{repo_id}/builds/{number}"
        headers = {"Authorization": f"Token token={self.api_token}"}

        resp = requests.get(target, headers=headers)
        json_resp = resp.json()

        id = json_resp["data"]["id"]
        number = json_resp["data"]["attributes"]["number"]
        state = json_resp["data"]["attributes"]["state"]

        return Build(id, repo_id, number, state)
    

    def get_latest_snapshot(self, github_slug: str):
        target = f"{_BASE_CODE_CLIMATE_URL}repos?github_slug={github_slug}"
        headers = {"Authorization": f"Token token={self.api_token}"}

        resp = requests.get(target, headers=headers)
        json_resp = resp.json()

        repo_id = json_resp["data"][0]["id"]
        snapshot_id = json_resp["data"][0]["relationships"][
            "latest_default_branch_snapshot"
        ]["data"]["id"]

        target = f"{_BASE_CODE_CLIMATE_URL}repos/{repo_id}/snapshots/{snapshot_id}"
        headers = {"Authorization": f"Token token={self.api_token}"}

        resp = requests.get(target, headers=headers)
        json_resp = resp.json()

        issue_count = int(json_resp["data"]["meta"]["issues_count"])

        return Snapshot(snapshot_id, repo_id, issue_count)

    def get_all_issues(self, snapshot: Snapshot) -> List[Issue]:
        all_issues = []
        for page in range(1, snapshot.pages + 1):
            target = f"{_BASE_CODE_CLIMATE_URL}repos/{snapshot.repo_id}/snapshots/{snapshot.id}/issues?page[number]={page}&page[size]={_PAGE_SIZE}"
            headers = {"Authorization": f"Token token={self.api_token}"}

            resp = requests.get(target, headers=headers)
            resp_json = resp.json()

            issues = resp_json["data"]
            for issue in issues:
                metric = issue["attributes"]["check_name"]
                aggregates_into = issue["attributes"]["categories"][0]
                all_issues.append(Issue(metric, aggregates_into))

        return all_issues

    def block_until_complete(self, build: Build):
        while build.state != "complete":
            build = self.get_build(build.number, build.repo_id)
            time.sleep(10)

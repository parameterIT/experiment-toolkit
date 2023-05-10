import requests
import time
import logging

from math import ceil
from typing import List
from requests.adapters import HTTPAdapter

import urllib3

_BASE_CODE_CLIMATE_URL = "https://api.codeclimate.com/v1/"
_PAGE_SIZE: int = 100


class Build:
    def __init__(self, id: str, repo_id: str, state: str, commit_sha: str, snapshot_id: str | None):
        self.id = id
        self.repo_id = repo_id
        self.state = state
        self.commit_sha = commit_sha
        self.snapshot_id = snapshot_id


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
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Token token={self.api_token}"})

        retry = urllib3.Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter=adapter)
        self.session.mount("https://", adapter=adapter)

    def get_id_for_repo(self, github_slug: str) -> str:
        """
        Returns the id associated with the given github_slug on code climate, assuming
        that the github_slug exists for the account associated with the api token
        """
        target = f"{_BASE_CODE_CLIMATE_URL}repos?github_slug={github_slug}"

        resp = self.session.get(target)
        json_resp = resp.json()
        repo_id = json_resp["data"][0]["id"]

        return repo_id

    def get_latest_snapshot(self, github_slug: str):
        target = f"{_BASE_CODE_CLIMATE_URL}repos?github_slug={github_slug}"

        resp = self.session.get(target)
        json_resp = resp.json()

        repo_id = json_resp["data"][0]["id"]
        snapshot_id = json_resp["data"][0]["relationships"][
            "latest_default_branch_snapshot"
        ]["data"]["id"]

        target = f"{_BASE_CODE_CLIMATE_URL}repos/{repo_id}/snapshots/{snapshot_id}"

        resp = self.session.get(target)
        json_resp = resp.json()

        issue_count = int(json_resp["data"]["meta"]["issues_count"])
        logging.info(issue_count)


        return Snapshot(snapshot_id, repo_id, issue_count)

    def get_snapshot_by_id(self, snapshot_id: str, repo_id: str):
        target = f"{_BASE_CODE_CLIMATE_URL}repos/{repo_id}/snapshots/{snapshot_id}"

        resp = self.session.get(target)
        json_resp = resp.json()

        issue_count = int(json_resp["data"]["meta"]["issues_count"])
        return Snapshot(snapshot_id, repo_id, issue_count)


    def get_all_issues(self, snapshot: Snapshot) -> List[Issue]:
        all_issues = []
        logging.info("Total issues is {}".format(snapshot.issue_count))
        for page in range(1, snapshot.pages + 1):
            target = f"{_BASE_CODE_CLIMATE_URL}repos/{snapshot.repo_id}/snapshots/{snapshot.id}/issues?page[number]={page}&page[size]={_PAGE_SIZE}"
            logging.info(f"Getting page {page}")

            resp = self.session.get(target)
            resp_json = resp.json()

            issues = resp_json["data"]
            for issue in issues:
                metric = issue["attributes"]["check_name"]
                aggregates_into = issue["attributes"]["categories"][0]
                all_issues.append(Issue(metric, aggregates_into))

        return all_issues

    def get_builds(self, repo_id: str) -> List[Build]:
        has_next = True
        target = f"{_BASE_CODE_CLIMATE_URL}repos/{repo_id}/builds?page[number]=1&page[size]=100"
        builds = []
        while has_next:
            resp = self.session.get(target)
            json_resp = resp.json()

            for b in json_resp["data"]:
                id = b["id"]
                state = b["attributes"]["state"]
                commit_sha = b["attributes"]["commit_sha"]
                snapshot_id = None
                if state == "complete":
                    snapshot_id = b["relationships"]["snapshot"]["data"]["id"]

                build = Build(id, repo_id, state, commit_sha, snapshot_id)
                builds.append(build)

            links = json_resp["links"]
            if "next" in links:
                has_next = True
                target = links["next"]
            else:
                has_next = False

        return builds

    def get_build_page(self, repo_id: str, page: int) -> List[Build]:
        target = f"{_BASE_CODE_CLIMATE_URL}repos/{repo_id}/builds?page[number]={page}&page[size]=100"
        builds = []
        resp = self.session.get(target)
        json_resp = resp.json()

        for b in json_resp["data"]:
            id = b["id"]
            state = b["attributes"]["state"]
            commit_sha = b["attributes"]["commit_sha"]
            snapshot_id = None
            if state == "complete":
                snapshot_id = b["relationships"]["snapshot"]["data"]["id"]

            build = Build(id, repo_id, state, commit_sha, snapshot_id)
            builds.append(build)

        return builds

import os
import sys
import requests
import logging
import time
import csv
import git

from pathlib import Path
from typing import Dict, List

ACCESS_TOKEN = os.getenv("CODE_CLIMATE_TOKEN")
CODE_CLIMATE_REPO = "parameterIT/testing"


def main():
    if ACCESS_TOKEN is None:
        logging.error("CODE_CLIMATE_TOKEN environment variable must be set")
        exit(1)

    if len(sys.argv) < 2:
        logging.error(
            "Usage: main.py <GITHUB_SLUG>, where GITHUB_SLUG is in the format 'username/reponame' on GitHub"
        )
        exit(1)

    git_folder: Path = Path("..") / Path("target") / Path(".git")

    github_slug = sys.argv[1]
    git.switch_repo(github_slug)

    tags = git.read_tags()
    print(tags)
    print(tags)
    git.iterate_over_tags(tags, work)


def work(tag: str):
    # Assumes that GitHub slug has a "global scope" that can be referenced through sys.argv[1]
    github_slug = sys.argv[1]

    block_while_build_is_running()
    results = {}
    locations = []

    for issue in get_issues():
        check_name = issue["attributes"]["check_name"]
        category = issue["attributes"]["categories"][0]
        try:
            results[check_name] = results[check_name] + 1
        except KeyError:
            results[check_name] = 1

        try:
            results[category] = results[category] + 1
        except KeyError:
            results[category] = 1

        location = issue["attributes"]["location"]
        # This fits with the .csv format: type, file, start, end
        locations.append(
            [check_name, location["path"], location["start_line"], location["end_line"]]
        )

    write_to_csv(results, locations, github_slug, tag)


def get_repo():
    """
    gets a repo from the github slug. github slug is a "username/reponame" format
    """
    target = f"https://api.codeclimate.com/v1/repos?github_slug={CODE_CLIMATE_REPO}"
    headers = {"Authorization": f"Token token={ACCESS_TOKEN}"}

    r = requests.get(target, headers=headers)
    return r.json()


def get_latest_build_snapshot():
    repo = get_repo()
    latest_build_snapshot = repo["data"][0]["relationships"][
        "latest_default_branch_snapshot"
    ]["data"]["id"]
    return latest_build_snapshot


def get_issues():
    repo_id = get_repo()["data"][0]["id"]
    snapshot_id = get_latest_build_snapshot()

    target = (
        f"https://api.codeclimate.com/v1/repos/{repo_id}/snapshots/{snapshot_id}/issues"
    )
    headers = {"Authorization": f"Token token={ACCESS_TOKEN}"}

    r = requests.get(target, headers=headers)
    return r.json()["data"]


def write_to_csv(results: Dict, locations: List, src_root: str, tag: str):
    # See https://docs.python.org/3/library/time.html#time.strftime for table
    # explaining formattng
    # Format: YYYY-MM-DD_HH-MM-SS
    current_time: str = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
    file_name = Path(current_time + ".csv")

    _write_metadata(file_name, src_root, tag)
    _write_results(file_name, results)
    _write_locations(file_name, locations)


def _write_metadata(file_name: Path, src_root: str, tag: str):
    file_location = Path("output") / Path("metadata") / file_name

    with open(file_location, "w") as metadata_file:
        writer = csv.writer(metadata_file)
        writer.writerow(["qualitymodel", "src_root"])
        writer.writerow(["actual code climate", f"{src_root}-{tag}"])


def _write_results(file_name: Path, results: Dict):
    file_location = Path("output") / Path("frequencies") / file_name

    with open(file_location, "w") as results_file:
        writer = csv.writer(results_file)
        writer.writerow(["metric", "value"])
        for description, value in results.items():
            writer.writerow([description, value])


def _write_locations(file_name: Path, locations: List):
    file_location = Path("output") / Path("locations") / file_name

    with open(file_location, "w") as locations_file:
        writer = csv.writer(locations_file)
        writer.writerow(["type", "file", "start", "end"])
        writer.writerows(locations)


def get_builds():
    repo_id = get_repo()["data"][0]["id"]

    target = f"https://api.codeclimate.com/v1/repos/{repo_id}/builds"
    headers = {"Authorization": f"Token token={ACCESS_TOKEN}"}

    r = requests.get(target, headers=headers)
    return r.json()["data"]


def block_while_build_is_running():
    should_check_builds = True
    while should_check_builds == True:
        builds = get_builds()
        should_check_builds = False
        for build in builds:
            if build["attributes"]["state"] == "running":
                should_check_builds = True
        time.sleep(5)


if __name__ == "__main__":
    main()

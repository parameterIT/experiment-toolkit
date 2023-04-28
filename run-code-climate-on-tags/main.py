import os
import sys
import logging
import time
import csv
import git


import code_climate

from pathlib import Path
from typing import Dict, List

USAGE_STRING = "Usage: main.py <Local Copy of Repository to Analyze> <GITHUB_SLUG> <Testing Repo>\nwhere GITHUB_SLUG is in the format 'username/reponame' on GitHub"

ACCESS_TOKEN = os.getenv("CODE_CLIMATE_TOKEN")
CODE_CLIMATE_REPO = "parameterIT/testing"


def main():
    logging.basicConfig(level=logging.INFO)

    if ACCESS_TOKEN is None:
        logging.error("CODE_CLIMATE_TOKEN environment variable must be set")
        exit(1)

    if len(sys.argv) != 4:
        logging.error("Incorrect number of arguments supplied")
        print(USAGE_STRING)
        exit(1)

    target_dir = Path(sys.argv[1])
    if not target_dir.exists():
        logging.error("Local copy of git repository does not exist")
        print(USAGE_STRING)
        exit(1)

    testing_repo = Path(sys.argv[3])
    if not testing_repo.exists():
        logging.error("Testing repository does not exist")
        print(USAGE_STRING)

    github_slug = sys.argv[2]
    git.switch_repo(testing_repo, github_slug)

    tags = git.read_tags(target_dir)
    git.iterate_over_tags(tags, work, testing_repo)


def work(tag: str):
    client: code_climate.Client = code_climate.Client(ACCESS_TOKEN)
    github_slug = sys.argv[2]

    repo_id = client.get_id_for_repo("parameterIT/testing")
    latest_build: code_climate.Build = client.get_latest_build_for(repo_id)
    logging.info(f"blocked by build {latest_build.id} with state {latest_build.state}")
    client.block_until_complete(latest_build)

    snapshot = client.get_latest_snapshot("parameterIT/testing")
    logging.info(f"latest snapshot {snapshot.id}")

    issues = client.get_all_issues(snapshot)
    results = {}
    locations = []
    for issue in issues:
        try:
            results[issue.metric] = results[issue.metric] + 1
        except KeyError:
            results[issue.metric] = 1

        try:
            results[issue.aggregates_into] = results[issue.aggregates_into] + 1
        except KeyError:
            results[issue.aggregates_into] = 1

    write_to_csv(results, locations, github_slug, tag)


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
    file_location = Path("output") / Path("outcome") / file_name

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


if __name__ == "__main__":
    main()

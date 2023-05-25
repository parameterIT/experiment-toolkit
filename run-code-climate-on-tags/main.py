import os
import sys
import logging
import time
import csv
import git

import code_climate

from pathlib import Path
from typing import Dict, List

USAGE_STRING = "Usage: main.py <Local Copy of Repository to Analyze> <GITHUB_SLUG_OF_REPO_TO_ANALYZE> <Testing Repo> <REMOTE_TESTING_REPO> \nwhere GITHUB_SLUG is in the format 'username/reponame' on GitHub"

ACCESS_TOKEN = os.getenv("CODE_CLIMATE_TOKEN")


def main():
    logging.basicConfig(level=logging.INFO)

    if ACCESS_TOKEN is None:
        logging.error("CODE_CLIMATE_TOKEN environment variable must be set")
        exit(1)

    if len(sys.argv) != 5:
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
    testing_github_slug = sys.argv[4]

    git.switch_repo(testing_repo, github_slug)

    tag_to_commit = git.tag_to_commit_mapping(target_dir)

    client: code_climate.Client = code_climate.Client(ACCESS_TOKEN)
    repo_id = client.get_id_for_repo(testing_github_slug)
    logging.info(f"Id for {testing_github_slug} is {repo_id}")
    builds = client.get_builds(repo_id)

    commits_with_no_builds = list(tag_to_commit.values())
    for _, commit in tag_to_commit.items():
        for build in builds:
            if build.commit_sha == commit:
                try:
                    commits_with_no_builds.remove(commit)
                except ValueError:
                    # Sometimes the list doesn't contain a commit, but since the exception is thrown because it should
                    # be removed its okay that its not there.
                    continue

    # Force the git repository to the tag.
    for commit in commits_with_no_builds:
        logging.info(
            f"{commit} is missing from builds, pushing it and waiting for the build to complete"
        )
        git.reset_repo(testing_repo, commit)

        # There are inconsistent timings on when the builds start
        # Get the first page of builds and see if it contains the commit sha, otherwise wait 10 seconds and try again
        is_build_complete = False
        while not is_build_complete:
            logging.info("Sleeping for 10 seconds...")
            time.sleep(10)
            # Builds are in chronological order, so newest one should be on the first page
            builds = client.get_build_page(repo_id, 1)
            for build in builds:
                logging.info(
                    f"Looking at build {build.id} for {build.commit_sha} with state {build.state}"
                )
                if build.commit_sha == commit and build.state == "complete":
                    is_build_complete = True

    # get builds again
    builds = client.get_builds(repo_id)

    for tag, commit in tag_to_commit.items():
        # Find the snapshot
        snapshot_id = ""
        for build in builds:
            if build.commit_sha == commit and build.state == "complete":
                snapshot_id = build.snapshot_id

        if snapshot_id == "":
            logging.error(f"No snapshot found for tag {tag} at {commit}, exiting...")
            exit(1)
        # Get all issues for that snapshot
        snapshot = client.get_snapshot_by_id(snapshot_id, repo_id)
        issues = client.get_all_issues(snapshot)
        logging.info(f"Got {len(issues)} for {tag} at {commit}")
        # Copy and paste the writing logic
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

        # Ensure that each file is written with at least 1 seconds between them as to not overwrite files
        time.sleep(1)
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
    file_location = Path("output") / Path("outcomes") / file_name

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

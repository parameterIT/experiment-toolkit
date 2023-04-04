import subprocess
from pathlib import Path
from typing import Callable, List


def read_tags():
    tags_out = subprocess.check_output(["cd ../../target && git tag -l"], shell=True)
    tags = [tag.decode("utf-8") for tag in tags_out.splitlines()]
    # Assumes versioning lexographical sort is chronological
    return tags


def switch_repo(github_slug: str):
    github_url = f"git@github.com:{github_slug}.git"

    subprocess.run(
        [f"cd ../../testing && git remote add target {github_url}"],
        shell=True,
    )
    subprocess.run(["cd ../../testing && git fetch target"], shell=True)
    subprocess.run(["cd ../../testing && git fetch target --tags"], shell=True)
    subprocess.run(["cd ../../testing && git checkout main"], shell=True)
    subprocess.run(["cd ../../testing && git reset --hard target/main"], shell=True)
    subprocess.run(["cd ../../testing && git push -f"], shell=True)


def reset_repo(commit: str):
    subprocess.run([f"cd ../../testing && git reset --hard {commit}"], shell=True)
    subprocess.run(["cd ../../testing && git push -f"], shell=True)


def iterate_over_tags(tags: List, action_between_tags: Callable):
    tags = tags[20:]
    for tag in tags:
        reset_repo(tag)
        action_between_tags(tag)

import subprocess
from pathlib import Path
from typing import Callable, List


def read_tags(dir_name: Path):
    tags_out = subprocess.check_output([f"cd {dir_name} && git tag -l"], shell=True)
    tags = [tag.decode("utf-8") for tag in tags_out.splitlines()]
    # Assumes versioning lexographical sort is chronological
    return tags


def switch_repo(testing_repo: Path, github_slug: str):
    github_url = f"git@github.com:{github_slug}.git"

    subprocess.run(
        [f"cd {testing_repo} && git remote remove target"],
        shell=True,
    )
    subprocess.run(
        [f"cd {testing_repo} && git remote add target {github_url}"],
        shell=True,
    )
    subprocess.run([f"cd {testing_repo} && git fetch target"], shell=True)
    subprocess.run([f"cd {testing_repo} && git fetch target --tags"], shell=True)
    subprocess.run([f"cd {testing_repo} && git checkout main"], shell=True)
    subprocess.run([f"cd {testing_repo} && git reset --hard target/main"], shell=True)
    subprocess.run([f"cd {testing_repo} && git push -f"], shell=True)


def reset_repo(testing_repo: Path, commit: str):
    subprocess.run([f"cd {testing_repo} && git reset --hard {commit}"], shell=True)
    subprocess.run([f"cd {testing_repo} && git push -f"], shell=True)


def iterate_over_tags(tags: List, action_between_tags: Callable, testing_repo: Path):
    tags = tags[20:]
    for tag in tags:
        reset_repo(testing_repo, tag)
        action_between_tags(tag)

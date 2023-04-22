#!/usr/bin/python3
import logging
import subprocess
import sys

from pathlib import Path

USAGE_STRING = "Usage: ./run-modu-on-tags.py PATH_TO_MODU_ROOT PATH_TO_TAGS_FOLDER"


def main():
    if not _is_valid_args():
        print(USAGE_STRING)
        exit(1)

    modu_path: Path = Path(sys.argv[1])
    tags_path: Path = Path(sys.argv[2])

    for tag in tags_path.iterdir():
        subprocess.run(
            f"cd {modu_path} && poetry run modu {tag.resolve()} code_climate --show-graphs=false",
            shell=True,
        )


def _is_valid_args() -> bool:
    if len(sys.argv) != 3:
        return False

    modu_path: Path = Path(sys.argv[1])
    if not modu_path.exists():
        logging.error(f"{modu_path} does not exist")
        return False

    tags_path: Path = Path(sys.argv[2])
    if not tags_path.exists():
        logging.error(f"{tags_path} does not exist")
        return False

    return True


main()

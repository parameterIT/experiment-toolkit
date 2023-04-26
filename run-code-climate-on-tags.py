#!/usr/bin/python3
import csv
import json
import logging
import time
import subprocess
import sys

from pathlib import Path
from typing import Dict, List

USAGE_STRING = "Usage: ./run-modu-on-tags.py PATH_TO_TAGS_FOLDER OUTPUT_FOLDER"


def main():
    if not _is_valid_args():
        print(USAGE_STRING)
        exit(1)

    tags_path: Path = Path(sys.argv[1])
    output_path: Path = Path(sys.argv[2])

    if not (output_path / Path("metadata")).exists():
        (output_path / Path("metadata")).mkdir()

    if not (output_path / Path("frequencies")).exists():
        (output_path / Path("frequencies")).mkdir()

    if not (output_path / Path("locations")).exists():
        (output_path / Path("locations")).mkdir()

    for tag in tags_path.iterdir():
        result = subprocess.run(
            f'cd {tag} && docker run --interactive --tty  --env CODECLIMATE_CODE="$PWD" --volume "$PWD":/code --volume /var/run/docker.sock:/var/run/docker.sock --volume /tmp/cc:/tmp/cc codeclimate/codeclimate analyze -f json',
            capture_output=True,
            shell=True,
        )

        code_climate_results = json.loads(result.stdout)
        modu_results, modu_locations = compute_count_per_metric(code_climate_results)
        write_to_csv(modu_results, modu_locations, tag.stem, output_path)


def _is_valid_args() -> bool:
    if len(sys.argv) != 3:
        return False

    tags_path: Path = Path(sys.argv[1])
    if not tags_path.exists():
        logging.error(f"{tags_path} does not exist")
        return False

    output_path: Path = Path(sys.argv[2])
    if not output_path.exists():
        logging.error(f"{output_path} does not exist")
        return False

    return True


def compute_count_per_metric(code_climate_results: List) -> tuple[Dict[str, int], List]:
    count_per_metric = {}
    locations = []
    for issue in code_climate_results:
        if issue["type"] != "issue":
            continue
        check_name = issue["check_name"]
        category = issue["categories"][0]
        try:
            count_per_metric[check_name] = count_per_metric[check_name] + 1
        except KeyError:
            count_per_metric[check_name] = 1

        try:
            count_per_metric[category] = count_per_metric[category] + 1
        except KeyError:
            count_per_metric[category] = 1

        location = issue["location"]
        # This fits with the .csv format: type, file, start, end
        locations.append(
            [
                check_name,
                location["path"],
                location["lines"]["begin"],
                location["lines"]["end"],
            ]
        )

    return count_per_metric, locations


def write_to_csv(results: Dict, locations: List, src_root: str, output_folder: Path):
    # See https://docs.python.org/3/library/time.html#time.strftime for table
    # explaining formattng
    # Format: YYYY-MM-DD_HH-MM-SS
    current_time: str = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
    file_name = Path(current_time + ".csv")

    _write_metadata(file_name, src_root, output_folder)
    _write_results(file_name, results, output_folder)
    _write_locations(file_name, locations, output_folder)


def _write_metadata(file_name: Path, src_root: str, output_folder: Path):
    file_location = output_folder / Path("metadata") / file_name

    with open(file_location, "w") as metadata_file:
        writer = csv.writer(metadata_file)
        writer.writerow(["qualitymodel", "src_root"])
        writer.writerow(["actual code climate", f"{src_root}"])


def _write_results(file_name: Path, results: Dict, output_folder: Path):
    file_location = output_folder / Path("frequencies") / file_name

    with open(file_location, "w") as results_file:
        writer = csv.writer(results_file)
        writer.writerow(["metric", "value"])
        for description, value in results.items():
            writer.writerow([description, value])


def _write_locations(file_name: Path, locations: List, output_folder: Path):
    file_location = output_folder / Path("locations") / file_name

    with open(file_location, "w") as locations_file:
        writer = csv.writer(locations_file)
        writer.writerow(["type", "file", "start", "end"])
        writer.writerows(locations)


main()

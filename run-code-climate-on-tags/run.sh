#!/usr/bin/env bash

set -a
source .env
set +a

mkdir -p output/frequencies
mkdir -p output/metadata
mkdir -p output/locations

poetry run python main.py $1

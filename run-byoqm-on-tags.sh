# Exit on first error
set -e

# Determine which repository to execute on

local_repo_path="../$1"

# Convert each tag to a directory
tags_dir="${local_repo_path}-tags"

rm -rf "$tags_dir"
mkdir -p "$tags_dir"

cd "$local_repo_path"
for tag in $(git tag)
do
  git checkout $tag
  new_dir="${tags_dir}/flask-${tag}"
  cp -r . "$new_dir"
  rm -f "${new_dir}/data_script.sh"
done

git checkout main

# Run byoqm on each flask folder
cd ../QualityTool

for flask_ver in $(ls ../flask-tags/)
do
  echo "Executing: poetry run main ${tags_dir}/${flask_ver} code_climate python --show-graphs=false"
  poetry run main "${tags_dir}/${flask_ver}" code_climate python --show-graphs=false
done 

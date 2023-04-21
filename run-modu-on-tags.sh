# Exit on first error
set -e

# Determine which repository to execute on
if [ $# -lt 2 ]; then
    echo "Too few arguments. Please refer to the README"
    exit 1
fi
if [ $# -gt 2 ]; then
    echo "Too many arguments. Please refer to the README"
    exit 1
fi

local_repo_path="../$1"

# Convert each tag to a directory
tags_dir="${local_repo_path}-tags"

rm -rf "$tags_dir"
mkdir -p "$tags_dir"

cd "$local_repo_path"
for tag in $(git tag)
do
  git checkout $tag
  new_dir="${tags_dir}/$1-${tag}"
  cp -r . "$new_dir"
  rm -f "${new_dir}/data_script.sh"
done

git checkout master

# Run modu on each flask folder
cd ../tool

for tag in $(ls ${tags_dir}/)
do
  echo "Executing: poetry run main ${tags_dir}/${tag} code_climate $2 --show-graphs=false"
  poetry run main "${tags_dir}/${tag}" code_climate $2 --show-graphs=false
done 

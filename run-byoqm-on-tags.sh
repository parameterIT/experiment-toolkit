# Exit on first error
set -e

# Convert each tag to a directory
flask_tags_dir="../flask-tags"

rm -rf "$flask_tags_dir"
mkdir -p "$flask_tags_dir"

for tag in $(git tag)
do
  git checkout $tag
  new_dir="${flask_tags_dir}/flask-${tag}"
  cp -r . "$new_dir"
  rm "${new_dir}/data_script.sh"
done

git checkout main

# Run byoqm on each flask folder
cd ../QualityTool

for flask_ver in $(ls ../flask-tags/)
do
  echo "Executing: poetry run main ../flask-tags/${flask_ver} code_climate python --show-graphs=false"
  poetry run main "../flask-tags/${flask_ver}" code_climate python --show-graphs=false
done 

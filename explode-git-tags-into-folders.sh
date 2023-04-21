# Exit on first error
set -e

USAGE_MSG="Usage: ./explode-git-tags-into-folders.sh PATH_TO_LOCAL_GIT_REPO TAGS_FOLDER REPO_NAME_FOR_TAG_FOLDERS"

# Check that all the arguments are passed
GIT_REPO="$1"
TAGS_FOLDER="$2"
REPO_NAME="$3"

if [ -z "$GIT_REPO" ]
then
  echo "ERROR: Path to local git repository not supplied"
  echo "$USAGE_MSG"
  exit
fi

if [ -z "$TAGS_FOLDER" ]
then
  echo "ERROR: Path to folder for storing each git tag not supplied"
  echo "$USAGE_MSG"
  exit
fi

if [ -z "$REPO_NAME"]
then
  echo "ERROR: Name of the repository to use when creating tag folders not supplied"
  echo "$USAGE_MSG"
  exit
fi

# Check that the arguments are valid
if [ ! -d "$GIT_REPO" ]
then
  echo "ERROR: '$GIT_REPO' does not exist"
  exit
fi

mkdir -p "$TAGS_FOLDER"

# Create a directory for each tag
cd "$GIT_REPO"
for TAG in $(git tag)
do
  git checkout "$TAG"
  NEW_DIR="$TAGS_FOLDER/$REPO_NAME-$TAG"
  cp -r . "$NEW_DIR"
done

set -e
#CWD=${PWD##*/}
DIR_PATH="$(dirname "${0}")"
IMG_REPO=$(cat ./README.md | grep "Docker:" | awk '{print $4}')
EXTPORT=$(cat ./README.md | grep "ExternalPort:" | awk '{print $4}')

echo $DIR_PATH $IMG_REPO $EXTPORT
docker build -t $IMG_REPO "$DIR_PATH"

set +e
# this is empty if the container crashes
echo $(docker ps -q -a --filter ancestor="$IMG_REPO" --format="{{.ID}}")
docker stop $(docker ps -q -a --filter ancestor="$IMG_REPO" --format="{{.ID}}")
set -e
docker run -p "$EXTPORT":"$EXTPORT" -d "$IMG_REPO"

## to debug - kill container and start with:
#docker run --restart unless-stopped -p "$EXTPORT":"$EXTPORT" "$IMG_REPO"

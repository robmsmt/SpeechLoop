#
##FOLDER=${PWD##*/}
##\ && echo "$FOLDER" > .INSTALLED
#
#IMG=$(cat ./README.md | grep "Docker:" | awk '{print $4}')
#docker run -d --restart unless-stopped -p 2800:2700 $IMG

set -e
#CWD=${PWD##*/}
DIR_PATH="$(dirname "${0}")"
IMG_REPO=$(cat "$DIR_PATH"/README.md | grep "Docker:" | awk '{print $4}')
EXTPORT=$(cat "$DIR_PATH"/README.md | grep "ExternalPort:" | awk '{print $4}')

docker build -t $IMG_REPO "$DIR_PATH"
set +e
docker stop $(docker ps -q -a --filter ancestor="$IMG_REPO" --format="{{.ID}}")
set -e
docker run -d "$IMG_REPO"
## to debug - kill container and start with:
#docker run --restart unless-stopped -p "$EXTPORT":"$EXTPORT" "$IMG_REPO"

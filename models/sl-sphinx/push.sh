#to upload
#docker push robmsmt/sl-sphinx-en-16k
# migrated to ghcr
DIR_PATH="$(dirname "${0}")"
IMG_REPO=$(cat "$DIR_PATH"/README.md | grep "Docker:" | awk '{print $4}')
docker push "$IMG_REPO"

#rm .INSTALLED
IMG=$(cat ./README.md | grep "Docker:" | awk '{print $4}')
echo "Killing: $IMG"
docker rm $(docker stop $(docker ps -a -q --filter ancestor="$IMG" --format="{{.ID}}"))
echo "Deleting: $IMG"
docker image rm "$IMG"
echo "Finished removing: $IMG"

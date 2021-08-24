
# try docker log first

# This should work for a running container
#
IMG=$(cat ./README.md | grep "Docker:" | awk '{print $4}')
ID=$(docker ps | grep $IMG | awk '{ print $1 }')

echo "INSPECTING: $IMG with ID: $ID"
$(docker stop $(docker ps -a -q --filter ancestor="$IMG" --format="{{.ID}}"))
docker commit "$ID" broken-container1 && docker run -p 3200:3200 -it broken-container1 /bin/bash
# run with: uvicorn main:app --host 0.0.0.0 --port 3200
# then hit test endpoint

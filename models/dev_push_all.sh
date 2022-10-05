
#source */build.sh

for i in ./sl-* ; do
  if [ -d "$i" ]; then
    cd "$i" && ./push.sh
    cd ..
  fi
done

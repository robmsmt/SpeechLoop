
#source */build.sh

for i in ./sl-* ; do
  if [ -d "$i" ]; then
    cd "$i" && ./build.sh
    cd ..
  fi
done

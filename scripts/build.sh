#!/bin/bash
SHA_PATH=.lib-sha

function check_for_changes() {
  current_sha=$(ls -alR ./lib | sha1sum)
  old_sha=$(cat $SHA_PATH)
  if [ -f "$dest/resume.zip" ] && [ "$current_sha" = "$old_sha" ]
  then
    echo "No changes in lib"
    exit 0
  else
    echo "$current_sha" > $SHA_PATH
  fi
}

function build_logging() {
  echo "Building logging package"
  build_dir=logging_build_dir

  if [ ! -d "$dest/$build_dir" ]; then
    mkdir -p $dest/$build_dir
  fi

  mkdir -p $dest/$build_dir/lib
  cp ./lib/log.py $dest/$build_dir/lib/
  (cd $dest/$build_dir && echo "Zipping: $(pwd)" && zip -Drq ../logging.zip ./*) || (echo "Failed to zip $dest/$build_dir" && exit 1)

  rm -r "${dest:?}/$build_dir"
}

function build_resume() {
  echo "Building resume package"
  build_dir=resume_build_dir

  if [ ! -d "$dest/$build_dir" ]; then
    mkdir -p $dest/$build_dir
  fi

  mkdir -p $dest/$build_dir/lib
  cp ./lib/*.* $dest/$build_dir/lib/
  uv pip install --quiet -r ./requirements/resume.txt --target $dest/$build_dir
  (cd $dest/$build_dir && echo "Zipping: $(pwd)" && zip -Drq ../resume.zip ./*) || (echo "Failed to zip $dest/$build_dir" && exit 1)
  rm -r "${dest:?}/$build_dir"
}

base=$(basename "$(pwd)")
# if [ "$base" != project ]; then
#   echo "Must be run from project root directory"
#   exit 1
# fi
if [ -z "$1" ]; then
  dest=./build
fi

check_for_changes
rm -r $dest 2> /dev/null
echo "Building function packages"
build_logging
build_resume
echo "Package builds complete"

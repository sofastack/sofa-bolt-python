#!/bin/sh
version=3.6.1
file=protoc-$version-linux-x86_64.zip
set -ex
if [ ! -f "$HOME/protobuf/bin/protoc" ]; then
  echo $PATH
  wget https://github.com/protocolbuffers/protobuf/releases/download/v$version/$file
  unzip $file -d $HOME/protobuf
else
  echo "Using cached directory."
fi

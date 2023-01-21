#!/bin/bash

set -euo pipefail

FILES=

while getopts e:b: option; do
  case $option in
    b) export BUCKET="$OPTARG";;
    f) FILES="$OPTARG $FILES";;
  esac
done

: $ENVIRONMENT

cd data
trap 'cd -' EXIT

[ -z "$FILES" ] && FILES=""$ENVIRONMENT-*""
for FILE in $FILES; do
  [[ $FILE = *backup ]] && continue
  aws s3 cp "$FILE" "s3://${BUCKET}/${ENVIRONMENT}/$FILE" --acl=private
done
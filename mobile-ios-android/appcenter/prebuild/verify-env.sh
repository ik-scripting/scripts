#!/usr/bin/env bash

ENV_PATH="$APPCENTER_SOURCE_DIRECTORY/.env"
ENV_SPEC_PATH="$APPCENTER_SOURCE_DIRECTORY/env.spec.json"

echo "Looking for .env at $ENV_PATH"

if ! [ -x "$(command -v jq)" ];
then
  echo "Error: jq is not installed and is required by this program"
  exit 1
fi

if [ ! -f "$ENV_PATH" ];
then
    echo "No .env file was created at $ENV_PATH"
    exit 1
fi

ENV_CONTENTS=$(cat $ENV_PATH)
jq -r ".[] | select(.required == true) | .key" "$ENV_SPEC_PATH" | while read REQUIRED_KEY; do
  if [[ ! "$ENV_CONTENTS" =~ $REQUIRED_KEY=[^[:space:]]+ ]];
  then
    echo "Required item $REQUIRED_KEY was not configured in .env. Stopping build now."
    exit 1
  fi
done

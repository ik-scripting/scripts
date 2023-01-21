#!/usr/bin/env bash

# Creates an .env from ENV variables for use with react-native-config
NATIVE_ENV_KEYS_PREFIX=${NATIVE_ENV_KEYS_PREFIX:-"^RN_"}
printf "Creating an .env file with the following:\n"
printf "%s\n" "$NATIVE_ENV_KEYS_PREFIX"
set | egrep -e "$NATIVE_ENV_KEYS_PREFIX" | sed 's/^RN_//g' > .env
printf "\n.env created with contents:\n\n"
cat .env

#!/bin/bash

set -e

# Read secrets into docker
# The docker environments needs to load secrets from a file.

# secrets-entrypoint.sh

# This will load all values from a secrets file and convert them into environment variables.
# If secret dir exists then export any variables in there to environment variables
# and pass to regular application startup script.
if [ -d "/secret" ] && [ "$(ls -A /secret)" ]; then
    echo "Load all secrets from file(s)..."
    eval $(cat /secret/* | sed 's/^/export /')
    echo "Done"
else
    echo 'No secret files found. Starting anyway...'
fi

# Call the regular CMD
exec "$@"
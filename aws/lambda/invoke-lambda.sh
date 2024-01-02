#!/usr/bin/env bash

set -euo pipefail

# https://docs.aws.amazon.com/cli/latest/reference/lambda/invoke.html

now="$(date --utc --iso-8601=seconds)"

echo "Invoke lambda"

aws lambda invoke --function-name $FUNCTION_NAME \
        --invocation-type Event \
        --cli-binary-format raw-in-base64-out \
        --payload '{ "name": "Bob" }' \
        response.json

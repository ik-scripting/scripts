#!/usr/bin/env bash
set -euo pipefail

# https://docs.aws.amazon.com/cli/latest/reference/s3api/put-bucket-notification-configuration.html

now="$(date --utc --iso-8601=seconds)"

echo "Trigger an Event. It will trigger an Event of S3 and should notify a lambda"

NOTIFICATION_CONFIGURATIONS='{"LambdaFunctionConfigurations":[{"Id":"'"$FUNCTION_NAME"'","LambdaFunctionArn":"'"$FUNCTION_ARN"'","Events":["s3:ObjectCreated:*"],"Filter":{"Key":{"FilterRules":[{"Name":"prefix","Value":"personalisation/recommendations/recommendationsV2"}]}}}]}'

aws s3api put-bucket-notification-configuration --bucket "$S3_BUCKET" \
        --notification-configuration "$NOTIFICATION_CONFIGURATIONS"

#!/bin/bash

set -euo pipefail

: $SOURCE_DIR
: $BUCKET
: $AWS_PROFILE
: $AWS_REGION

sync_artifacts() {
  scripts/save_state.sh -e $ENVIRONMENT -f $STATE_GLOBAL -b $STATE_BUCKET
  terraform state list -state="data/$STATE_GLOBAL" > parameters/$ENVIRONMENT/created-resources
  rm -f data/$STATE_GLOBAL
  rm -f data/$STATE_GLOBAL.*
}
# trap save_state EXIT

aws s3 cp $SOURCE_DIR s3://$BUCKET/prod-images/ --recursive
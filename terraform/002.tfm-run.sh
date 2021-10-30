#!/bin/bash

set -eu
set -o pipefail

: "${AWS_REGION}"
: "${AWS_STATE_BUCKET}"
: "${AWS_ACCOUNT_ID}"
: "${ENVIRONMENT}"
: "${DNS_DOMAIN}"

# DECRYPTED=$(sops -d "vault/values.${ENVIRONMENT}.enc.yaml")

while getopts s:c: option; do
  case "${option}" in
  s) export STEP=${OPTARG};;
  c) export COMMAND=${OPTARG};;
  \? ) echo "Usage: aws.terraform.sh [-s STEP] [-c COMMAND]";;
  : ) echo "Invalid option: $OPTARG requires an argument" 1>&2;;
  esac
done

PREFIX=${PREFIX}
OPTS=
[ "$COMMAND" = plan ] || OPTS="-parallelism=5"

rm -f .terraform/terraform.tfstate

clean_up() {
  rm -f .terraform/terraform.tfstate
  echo "cleanup if anything.."
}
trap clean_up EXIT

STATE_FILE="state.tfstate"
MODULE="infra/aws/$STEP"
# TF_VARS_STEP="inventory/${STEP}.${ENVIRONMENT}.tfvars"

export TF_VAR_prefix="${PREFIX}"
export TF_VAR_region="${AWS_REGION}"
export TF_VAR_states_bucket="${AWS_STATE_BUCKET}"
export TF_VAR_dns_domain="${DNS_DOMAIN}"
export TF_VAR_target_account_id="${AWS_ACCOUNT_ID}"
export TF_VAR_environment="${ENVIRONMENT}"

terraform init \
  -backend-config="bucket=${AWS_STATE_BUCKET}" \
  -backend-config="workspace_key_prefix=${STEP}" \
  -backend-config="key=${ENVIRONMENT}/${STEP}/${STATE_FILE}" \
  -backend-config="encrypt=true" \
  -backend-config="region=${AWS_REGION}" \
  -backend-config="profile=${AWS_PROFILE}" \
  -backend-config="skip_credentials_validation=true" \
  -backend-config="skip_get_ec2_platforms=true" \
  -backend=true -get=true \
  -reconfigure \
  "${MODULE}"

terraform "${COMMAND}" "${OPTS}" \
  -refresh=true "${MODULE}"
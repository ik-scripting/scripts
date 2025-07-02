#!/usr/bin/env bash

set -eu

LIGHT_BLUE="\033[1;34m"
RED="\e[31m"
RESET="\e[0m"

: "${ENV}"
: "${REGION}"

# Get the lock table
case "${ENV}" in
  "audit")
    LOCK_TABLE="terraform-state-lock-0000"
  ;;
  "billing")
    LOCK_TABLE="terraform-state-lock-00000"
  ;;
  "contact-center-dev")
    LOCK_TABLE="terraform-state-lock-0000"
  ;;
  "contact-center-prod")
    LOCK_TABLE="terraform-state-lock-0000"
  ;;
  "container-registry")
    LOCK_TABLE="terraform-state-lock-0000"
  ;;
  "datalake")
    LOCK_TABLE="terraform-state-lock-0000"
  ;;
  "dev")
    LOCK_TABLE="terraform-state-lock-0000"
  ;;
  "dr-backups")
    LOCK_TABLE="terraform-state-lock-0000"
  ;;
  "experimentation")
    LOCK_TABLE="terraform-state-lock-0000"
  ;;
  "lab-security")
    LOCK_TABLE="terraform-state-lock-0000"
  ;;
  "networks")
    LOCK_TABLE="terraform-state-lock-0000"
  ;;
  "prod")
    LOCK_TABLE="terraform-state-lock-0000"
  ;;
  "retail-admin")
    LOCK_TABLE="terraform-state-lock-0000"
  ;;
  "sandbox")
    LOCK_TABLE="terraform-state-lock-0000"
  ;;
  "security-dev")
    LOCK_TABLE="terraform-state-lock-0000"
  ;;
  "security-prod")
    LOCK_TABLE="terraform-state-lock-0000"
  ;;
  "security-sandbox")
    LOCK_TABLE="terraform-state-lock-0000"
  ;;
  "services")
    LOCK_TABLE="terraform-state-lock-0000"
  ;;
  *)
    echo -e "${RED}Unsupported env: ${ENV}${RESET}"
    exit 1
  ;;
esac

# Check if at least action has been supplied
if [[ -z $LOCK_ID_PATH ]] && [[ -z $COMPONENT ]]; then
  echo -e "${RED}LOCK_ID_PATH or COMPONENT must be supplied${RESET}"
  exit 1
fi

echo -e "${LIGHT_BLUE}Env: ${ENV} | Region: ${REGION}${RESET}"

# If LOCK_ID_PATH given. Search for it.
if [[ -n $LOCK_ID_PATH ]]; then
  item=$(aws dynamodb get-item --region $REGION \
    --table-name $LOCK_TABLE \
    --key '{"LockID": {"S": "'${LOCK_ID_PATH}'"}}')

  # If item doesn't exist - fail
  if [[ -z $item ]]; then
    echo -e "${RED}Lock path $LOCK_ID_PATH not found${RESET}"
    exit 1
  fi

  # else delete the item.
  aws dynamodb delete-item --region $REGION \
    --table-name $LOCK_TABLE \
    --key '{"LockID": {"S": "'${LOCK_ID_PATH}'"}}'

  echo -e "Lock ${LIGHT_BLUE}${LOCK_ID_PATH}${RESET} deleted"

elif [[ -n $COMPONENT ]]; then
  echo -e "Unlocking any TF states in the ${LIGHT_BLUE}${COMPONENT}${RESET} component"
  # Find all locked states for the given component. These will have the `info` attribute.
  lock_paths=$(aws dynamodb scan --region $REGION \
    --table-name $LOCK_TABLE \
    --projection-expression 'LockID' \
    --filter-expression 'contains(LockID, :comp) AND attribute_exists(Info)' \
    --expression-attribute-values '{":comp": {"S": "'${COMPONENT}'"}}' \
    --query 'Items[*].LockID.S' \
    --output text)

  if [[ -z $lock_paths ]]; then
    echo "No locks to delete"
    exit 0
  fi

  # Delete all the items
  for lock_path in $lock_paths; do
    aws dynamodb delete-item --region $REGION \
      --table-name $LOCK_TABLE \
      --key '{"LockID": {"S": "'${lock_path}'"}}'
    echo "Lock $lock_path deleted"
  done
  echo "All locks deleted"
fi

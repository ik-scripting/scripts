#!/bin/bash

# Prerequisite
# 1. AWS Credentials
# 2. KUBECONFIG set

set -e

count=0
not_equal_count=0
for el in `helm ls --short | xargs`
do
  ((count=count+1))
  set +e
  helm get values $el -o yaml | yq -r '.env' > result/$el.yaml
  set -e
  result=$(helm get values $el -o yaml)

  if [[ $result =~ "DD_SERVICE_NAME" ]]; then
    echo "N:$count. Command: helm get values $el. DD_SERVICE_NAME is set"
    SERVICE_NAME=$(helm get values $el -o yaml | yq -r '.name')
    DD_SERVICE_NAME=$(helm get values $el -o yaml | yq -r '.env.DD_SERVICE_NAME')
    echo -e "\tHELM CHART NAME: $el"
    echo -e "\tSERVICE NAME: $SERVICE_NAME"
    echo -e "\tDD_SERVICE_NAME: $DD_SERVICE_NAME"
    ((count=count+1))
    if [[ $SERVICE_NAME != $DD_SERVICE_NAME ]];then
      echo -e "\t\tNOT EQUAL"
      ((not_equal_count=not_equal_count+1))
    fi
  # else
  #   echo "N:$count. Command: helm get values $el. DD_SERVICE_NAME not set"
  fi
done

echo "NUMBER of services with explicit DD_SERVICE_NAME: $count"
echo "NUMBER of services with explicit DD_SERVICE_NAME where NAME does not match DD_SERVICE_NAME: $not_equal_count"

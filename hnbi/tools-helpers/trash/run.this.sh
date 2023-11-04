#!/bin/bash

ENVS=(
  assets-api-helm-7cdc95589c-wn2zg
aurora-331-helm-8479db74d-wkbhl
aurora-fix-cc-helm-c8849c877-wbgkg)


for el in "${ENVS[@]}" ; do
  echo "kubectl delete pod $el"
  kubectl delete pod $el
  echo "sucess"
done

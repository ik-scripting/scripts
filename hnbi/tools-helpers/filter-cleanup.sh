#!/bin/bash

# Prerequisite
# 1. AWS Credentials
# 2. KUBECONFIG set

set -e

excluded=(
    "product-search-page-helm"
    "product-search-page-nl-helm"
    "product-search-page-be-fr-helm"
)

function array_contains { # arrayname value
  local -A _arr=()
  local IFS=
  eval _arr=( $(eval printf '[%q]="1"\ ' "\${$1[@]}") )
  return $(( 1 - 0${_arr[$2]} ))
}

count=0
for el in `helm ls --all --short --filter "product-search-page" | xargs`
do
    if printf '%s\n' "${excluded[@]}" | grep -x -q "$el"; then
        echo "skip: $el"
    else
        ((count=count+1))
        echo "N:$count. Command: helm uninstall $el --wait"
        helm uninstall "$el" --dry-run --wait
        if [ $? -ne 0 ]; then
            echo "ERROR: not able to delete $el"
            exit 1
        fi
    fi
done

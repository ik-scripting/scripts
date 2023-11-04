#!/bin/bash

# bin/k8s-ports.sh

# kubectl get deploy -o jsonpath="{.items[*].spec.template.spec.containers[*].ports.}"
# kubectl get deploy -o jsonpath="{.items[*].spec.template.spec.containers[*].ports[*].containerPort}" |\
# tr -s '[[:space:]]' '\n' |\
# sort |\
# uniq -c

# kubectl get pods --all-namespaces -o jsonpath="{.items[*].spec.containers[*].image}" |\
# tr -s '[[:space:]]' '\n' |\
# sort |\
# uniq -c

# kubectl get deploy -o jsonpath="{.items[*].spec.template.spec.containers[*].ports}"
# kubectl get deploy -o jsonpath="{.items[*].spec.containers[*].ports[*].containerPort}"

excluded=(
  "cron"
)

count=0
for el in `helm ls --all --short | xargs`
do
    if printf '%s\n' "${excluded[@]}" | grep -x -q "$el"; then
        echo "skip: $el"
    else
        ((count=count+1))
        set +e
        helm get values $el -o yaml | yq -r '.env' > result/$el.yaml
        set -e

        result=$(helm get values $el -o yaml)
        
        helm uninstall "$el" --dry-run --wait
        if [ $? -ne 0 ]; then
            echo "ERROR: not able to delete $el"
            exit 1
        fi
    fi
done

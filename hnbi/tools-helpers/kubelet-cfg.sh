#!/bin/bash

# Prerequisite
# 1. AWS Credentials
# 2. KUBECONFIG set
# ./bin/kubelet-cfg.sh
# WHy script exist: https://gitlab.com/HnBI/platform-as-a-service/infrastructure/-/merge_requests/2162

# What it does
# 1. Make a request to kubelet
# 2. Write to file kubelet configs for different types of workers

set -e

ENVS=(
  "example:$(kubectl get node --selector='dedicated=dummy' --output=jsonpath={.items..metadata.name})"
  "worker:$(kubectl get node --selector='dedicated=worker' --output=jsonpath={.items..metadata.name} | awk '{print $1}')"
)

for el in "${ENVS[@]}" ; do
    KEY="${el%%:*}"
    NODE_ID="${el##*:}"
    printf "%s::%s\n" "$KEY" "$NODE_ID"
    kubectl get --raw=/api/v1/nodes/$NODE_ID/proxy/configz | python3 -m json.tool > fixtures/$KEY.json
done

cat fixtures/*.json | grep kubeReserved -A 3
cat fixtures/*.json | grep systemReserved -A 3
cat fixtures/*.json | grep evictionHard -A 3

kubectl get deployment cluster-autoscaler --namespace kube-system -o yaml | yq -r '.spec.template.spec.containers[0].image | split(":").[-1]'
kubectl get deployment cluster-autoscaler --namespace kube-system --output=jsonpath={.spec.template.spec.containers[0].image}
kubectl get deployment cluster-autoscaler --namespace kube-system --output=jsonpath={..image}

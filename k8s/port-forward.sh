#!/bin/bash

# Multiple endpoints
# https://kubernetes.github.io/dashboard/docs/user/access-control/creating-sample-user.html
# https://kubernetes.github.io/dashboard/

set -euo pipefail

: "${KUBECONFIG}"

echo -e "Token"
kubectl -n monitoring describe secret "$(kubectl -n monitoring get secret | grep operator | awk '{print $1}')"
echo -e "\n"

K8S_DASHBOARD_PORT=8443
echo -e "dashboard >> https://localhost:${K8S_DASHBOARD_PORT}"
kubectl port-forward -n monitoring svc/kubernetes-dashboard "${K8S_DASHBOARD_PORT}" &
echo -e "\n"
K8S_PROCESS=$!


OPS_PORT=8099
echo -e "kube-ops-view >> http://localhost:${OPS_PORT}"
kubectl port-forward -n monitoring svc/kube-ops-view $OPS_PORT:80 &
echo -e "\n"
OPS_PROCESS=$!

echo -e "\npress ctrl-c to stop\n"
echo -e "\n"

wait $K8S_PROCESS \
  $OPS_PROCESS

set -x
lsof -i:${K8S_DASHBOARD_PORT}
lsof -i:${OPS_PORT}
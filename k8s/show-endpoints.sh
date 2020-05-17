#!/usr/bin/env bash

set -euo pipefail

: $ENVIRONMENT
: $KUBECONFIG
: $AWS_PROFILE

echo -e "\nGet token for Kubernetes Dashboard: \n"
kubectl -n monitoring describe secret $(kubectl -n monitoring get secret | awk '/^kubernetes-dashboard-token-/{print $1}') | awk '$1=="token:" {print $2}'
echo -e "\n"

KUBEDASHBOARD_PORT=8443
echo "Kubernetes dashboard >> https://localhost:$KUBEDASHBOARD_PORT/ "
kubectl -n monitoring port-forward svc/kubernetes-dashboard $KUBEDASHBOARD_PORT:443 &
KUBEDASHBOARD_PROCESS=$!

PROMETHEUS_PORT=9090
echo "Prometheus >> http://localhost:$PROMETHEUS_PORT/ "
kubectl port-forward -n monitoring svc/prometheus-prometheus $PROMETHEUS_PORT &
PROMETHEUS_PROCESS=$!

KUBEHEALTHY_PORT=8002
echo "Kuberhealthy >> http://localhost:$KUBEHEALTHY_PORT/ "
kubectl -n monitoring port-forward svc/kuberhealthy $KUBEHEALTHY_PORT:80 &
KUBERHEALTHY_PROCESS=$!

echo "Grafana admin password >> Check Pipeline for Hint <<"
GRAFANA_PORT=9080
echo "Grafana Dashboard: http://localhost:$GRAFANA_PORT"
kubectl port-forward -n monitoring svc/prometheus-grafana $GRAFANA_PORT:80 &
GRAFANA_PROCESS=$!

HEAPSTER_PORT=8082
echo "Heapster >> http://localhost:$HEAPSTER_PORT"
kubectl port-forward -n monitoring svc/heapster $HEAPSTER_PORT &
HEAPSTER_PROCESS=$!

OPS_VIEW_PORT=8083
echo "Ops View Dashboard >> http://localhost:$OPS_VIEW_PORT"
kubectl port-forward -n monitoring svc/kube-ops-view-kube-ops-view $OPS_VIEW_PORT:80 &
OPS_VIEW_PROCESS=$!

METRICS_SERVER_PORT=9443
echo "Metrics Server >> https://localhost:$METRICS_SERVER_PORT"
kubectl port-forward -n monitoring svc/metrics-server $METRICS_SERVER_PORT:443 &
METRICS_SERVER_PROCESS=$!

ALERT_MANAGER_PORT=9093
echo "Alert Manager >> http://localhost:$ALERT_MANAGER_PORT"
kubectl port-forward -n monitoring svc/prometheus-alertmanager $ALERT_MANAGER_PORT &
ALERT_MANAGER_PROCESS=$!

echo -e "\npress ctrl-c to stop\n"
echo -e "\n"

wait $PROMETHEUS_PROCESS \
$KUBEDASHBOARD_PROCESS \
$KUBERHEALTHY_PROCESS \
$GRAFANA_PROCESS \
$HEAPSTER_PROCESS \
$OPS_VIEW_PROCESS \
$METRICS_SERVER_PROCESS \
$ALERT_MANAGER_PROCESS

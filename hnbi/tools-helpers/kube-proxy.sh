#!/bin/bash

# Prerequisite
# 1. AWS Credentials
# 2. KUBECONFIG set
# ./kube-proxy.sh
# WHy script exist: https://gitlab.com/HnBI/platform-as-a-service/infrastructure/-/merge_requests/2162

# What it does
# 1. Open a tunnel between localhost and the Kubernetes API serve

set -e

kubectl proxy

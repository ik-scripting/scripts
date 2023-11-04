#!/bin/bash

# /bin/deploy-node-termination.sh

HELM_VALUES=~/workspace/hb/paas/k8s-cluster-config/core-services/helm-values/aws-node-termination-handler.yaml

HELM_CHART_VERSION="0.15.1"

helm diff upgrade aws-node-termination-handler eks-charts/aws-node-termination-handler \
      --suppress-secrets \
      --allow-unreleased \
      --values ${HELM_VALUES}\
      --namespace kube-system \
      --version ${HELM_CHART_VERSION}

helm upgrade aws-node-termination-handler eks-charts/aws-node-termination-handler \
      --install \
      --atomic \
      --namespace kube-system \
      --logtostderr \
      --timeout '20m' \
      --version ${HELM_CHART_VERSION} \
      --values ${HELM_VALUES}
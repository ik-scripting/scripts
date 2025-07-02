#!/usr/bin/env bats

set -o pipefail
load helper

@test "kubecontext should be set" {
  run kubectl config current-context
  # TODO environment variable to use e.g. cluster/eks-cluster-$ENVIRONMENT
  assert_output --partial "cluster/eks-cluster"
}

@test "default namespaces should have no apps" {
  run kubectl get pods -n default
  assert_line 'No resources found in default namespace.'
}

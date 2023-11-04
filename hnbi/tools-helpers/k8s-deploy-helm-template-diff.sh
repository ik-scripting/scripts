#!/usr/bin/env bash

# diffs rendered k8s manifests from two k8s-deploy repository locations.
# Useful when one of them is checked out in an experimental branch and the other to a stable commit/tag.
# Requires a set of values files stored in $VALUES_DIR

WORKDIR=$HOME/Projects
VALUES_DIR=$WORKDIR/k8s-deploy/test-values/
STABLE_K8S_DEPLOY=k8s-deploy-master
EXPERIMENTAL_K8S_DEPLOY=k8s-deploy

render() {
  values=$1
  k8s_deploy_dir=$2
  helm template \
      deployment-test $WORKDIR/$k8s_deploy_dir/k8s/helm/hbi-deployment \
      --values $WORKDIR/$k8s_deploy_dir/k8s/helm/hbi-deployment/values.yaml \
      --values $VALUES_DIR/$values \
      --namespace apps --set team=test
}

for file in $(ls $VALUES_DIR/*.yaml); do
  file=$(basename $file)
  echo "##################################################################################"
  echo "  Doing diff for $file"
  diff <(render $file $STABLE_K8S_DEPLOY) <(render $file $EXPERIMENTAL_K8S_DEPLOY) -u
  echo ""
  echo "##################################################################################"
  echo ""
done

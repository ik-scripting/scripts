#!/usr/bin/env bash

set -eou pipefail

SECRET_NAME=traefik-tls-cert
NAMESPACES=(apps datalake kube-system vault)

check_secret() {
  local namespace=$1

  echo "Displaying certificate from $SECRET_NAME in $namespace namespace"
  kubectl get secret/$SECRET_NAME -n $namespace -o jsonpath='{.data}' | jq '."tls.crt"' -r | base64 --decode | openssl x509 -text
}

check_tlsstore() {
  local namespace=$1

  echo "Checking that TLSStore/default in $namespace namespace contains $SECRET_NAME"
  kubectl get tlsstore/default -n $namespace -o jsonpath='{.spec}' | grep \"secretName\":\"$SECRET_NAME\"
}

copy_secret() {
  local source_namespace=$1
  local destination_namespace=$2

  local secret=$(kubectl get secret $SECRET_NAME -n $source_namespace -o=json | jq 'del(.metadata.resourceVersion,.metadata.uid,.metadata.selfLink,.metadata.creationTimestamp,.metadata.annotations,.metadata.generation,.metadata.ownerReferences,.metadata.namespace)')

  echo "Applying secret $SECRET_NAME from $source_namespace to $destination_namespace"
  echo $secret | yq eval - -P | kubectl apply -n $destination_namespace -f -
}

cleanup_secrets() {
  echo "Cleaning up $SECRET_NAME from ${NAMESPACES[@]}"
  read -p "Continue? (YES/NO): " confirm
  [[ $confirm == "YES" ]] || (echo Exiting... && exit 1)

  for namespace in "${NAMESPACES[@]}"; do
    echo "deleting secret/$SECRET_NAME from $namespace"
    kubectl delete secret/$SECRET_NAME -n $namespace
  done
}

rollback_secrets() {
  local source_namespace=$1

  echo "Secret $SECRET_NAME from $source_namespace will be copied to ${NAMESPACES[@]}"
  read -p "Continue? (YES/NO): " confirm
  [[ $confirm == "YES" ]] || (echo Exiting... && exit 1)

  for namespace in "${NAMESPACES[@]}"; do
    copy_secret $source_namespace $namespace || true
  done

}

ACTION=$1
case $ACTION in
  copy-to-ingress)
    copy_secret apps ingress
    check_secret ingress
    ;;
  cleanup)
    check_secret ingress || (echo "No $SECRET_NAME secret found in ingress namespace! aborting secret cleanup in other namespaces" && exit 1)
    check_tlsstore ingress || (echo "No valid TLSStore found in ingress namespace! aborting secret cleanup in other namespaces" && exit 1)
    cleanup_secrets
    ;;
  rollback)
    check_secret ingress || (echo "No $SECRET_NAME secret found in ingress namespace! aborting secret cleanup in other namespaces" && exit 1)
    rollback_secrets ingress
    ;;
  *)
    echo invalid action
    ;;
esac

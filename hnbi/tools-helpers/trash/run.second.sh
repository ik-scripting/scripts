#!/bin/bash

# k get pods | grep beyond | grep '0/1' | awk '{print $1}' > another.one.sh

ENVS=(beyond-go-diag-207-add-file-refs-helm-7bb6856476-nltpf
beyond-go-diag-479-impl-test-reg-form-helm-768fbfbbd-pnbxp
)

for el in "${ENVS[@]}" ; do
  echo "kubectl delete pod $el"
  kubectl delete pod $el
  echo "sucess"
done

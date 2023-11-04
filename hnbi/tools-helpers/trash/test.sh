#!/bin/bash

# get images names
# k get pods | grep beyond | grep '0/1' | awk '{print $1}' > pods

ENVS=(beyond-go-diag-207-add-file-refs-helm-7bb6856476-dzd58
beyond-go-diag-479-impl-test-reg-form-helm-768fbfbbd-srdqm
beyond-go-diag-484-testkit-email-helm-75f45d4797-b6dqw)

for el in "${ENVS[@]}" ; do
  kubectl get pod $el -o jsonpath='{..image}' | awk '{print $1}'
  echo
done

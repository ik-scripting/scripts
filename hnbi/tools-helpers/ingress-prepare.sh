#!/bin/bash

# Prerequisite
# 1. AWS Credentials
# 2. KUBECONFIG set
# WHy script exist: https://hbidigital.atlassian.net/wiki/spaces/PAAS/pages/5477531649/Incident+Report+11+03+2022+Traefik+ExternalService+outage+and+k8s-deploy+issues+in+dev

# What it does
# Read all ingresses in apps namespace, create backup copy, sanitize outdated Ingressroutes e.g. with middlware: nulls and fix them
# kubectl patch can be more performant, but in our case, if somethign happens, we can easy debug it, as all the files awailable.
# Note: the script only update broken Ingresses, this should reduce the blast radius

ENV=prod-28-applied

set -e

function array_contains { # arrayname value
  local -A _arr=()
  local IFS=
  eval _arr=( $(eval printf '[%q]="1"\ ' "\${$1[@]}") )
  return $(( 1 - 0${_arr[$2]} ))
}

count=0

process() {
for el in `kubectl get IngressRoute -o name -n apps`
do
    ((count=count+1))
    resource=${el##*ingressroute.traefik.containo.us/}
    echo $resource
    kubectl get IngressRoute $resource -n apps -o yaml | kubectl neat > apps/$ENV/any/$resource.yml
    if [[ "$(cat apps//$ENV/any/$resource.yml)" == *"middlewares: null"* ]]; then
      cp apps//$ENV/any/$resource.yml apps/$ENV/before/$resource.yml
      # remove lines that contain middlewares and create new file
      sed '/middlewares/d' apps//$ENV/before/$resource.yml > apps/$ENV/after/$resource.yml
    fi
    if [ $? -ne 0 ]; then
        echo "ERROR: not able to delete $el"
        exit 1
    fi
done
}

# apply changes
apply() {
  count=0
  for el in `ls -lA apps/$ENV/after | awk -F':[0-9]* ' '/:/{print $2}'`
  do
      ((count=count+1))
      echo "kubectl apply -f apps/after/$el"
      kubectl apply -f apps/$ENV/after/$el # --dry-run=client
      echo $count
      if [ $? -ne 0 ]; then
          echo "ERROR: not able to delete $el. count: $count"
          exit 1
      fi
  done
  echo $count
}

total() {
  # echo total number of ingresses in apps namespace
  kubectl get IngressRoute -n apps | wc -l
}

cleanup() {
  rm apps/after/*
  rm apps/any/*
  rm apps/before/*
}

usage() { echo "Usage: $0 [-p process] [-p apply]"; exit 1; }

for _ in "$@"; do
    case $1 in
        -p|--process) process; shift ;;
        -a|--apply) apply; shift ;;
        -c|--cleanup) cleanup; shift ;;
        -t|--total) total; shift ;;
        *) usage;;
    esac
    shift
done

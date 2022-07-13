#!/bin/bash

# ./push-metrics.sh "LightHouse" metric.json
# aws-vault exec $profile -- ./push-metrics.sh -n "WebPerformanceDegradation" -d lighthouse.json
# aws-vault exec $profile -- ./push-metrics.sh -n "ApiPerformanceDegradation" -d performance.json
# https://aws.amazon.com/premiumsupport/knowledge-center/cloudwatch-push-custom-metrics/

usage() { echo "Usage: $0 [-n <Lighthouse|Performance>] [-d <metric.json>]" 1>&2; exit 1; }

while getopts ":n:d:" option; do
  case $option in
    n) NAMESPACE="$OPTARG";;
    d) METRICS="$OPTARG";;
    *) usage;;
  esac
done

aws cloudwatch put-metric-data --namespace "${NAMESPACE}" --metric-data file://$METRICS

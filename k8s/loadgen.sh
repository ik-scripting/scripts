#!/usr/bin/env bash

echo "example app: http://localhost:18080/metrics"
kubectl port-forward -n loadgen-temp svc/loadgen-app 18081:8080 &
LOADGEN_APP_PROCESS=$!

sleep 3

for i in {1..500}
do
   curl -s http://127.0.0.1:18081/api/foo > /dev/null
   sleep 5
done

for i in {1..500}
do
   curl -s http://127.0.0.1:18081/api/bar > /dev/null
   sleep 5
done

kill -9 $LOADGEN_APP_PROCESS

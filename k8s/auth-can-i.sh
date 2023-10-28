#!/usr/bin/env bash

kubectl auth can-i delete pod --as=hbi:team:composer-platform -n apps-composer

kubectl auth can-i delete pod --as=hbi:team:composer-platform --as=hbi:team:alldevs

kubectl auth can-i --list --namespace=apps-composer --as=hbi:team:composer-platform
kubectl auth can-i get pods --as=hbi:team:composer-platform
kubectl auth can-i delete pods --as=hbi:role:delete
k auth can-i get pods -n=apps --as=hbi:team:composer-platform

kubectl auth can-i delete pods -n=apps-composer --as-group=hbi:team:composer-platform
kubectl auth can-i delete pods -n=apps-composer --as-group=hbi:team:composer-platform


kubectl auth can-i --list -n=apps-composer --as-group=hbi:team:composer-platform --as=team-composer

kubectl auth can-i delete pods -n=apps-composer --as-group=hbi:team:composer-platform  --as=team-composer

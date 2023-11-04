#!/bin/bash


k get pods --selector apm=enabled
k get pods --selector apm=disabled
k get pods --selector service-type=deployment
k get pods --selector service-type=cron
k get pods | grep beyond-go
kubectl exec deploy/nginx-deployment -- date

# helm list --filter homepage-content

#!/bin/bash

kubectl -n ingress port-forward service/traefik-internal-v2-web-ui 8080:80
kubectl -n ingress port-forward service/traefik-external-v2-web-ui 8080:80

helm uninstall spring-cloud-config-server-helm


k describe clusterrolebindings system:discovery
k edit clusterrolebindings system:discovery

k describe clusterrolebindings system:public-info-viewer
k edit clusterrolebindings system:public-info-viewer
k get pods --selector component=server -o=custom-columns=NODE:.spec.nodeName,NAME:.metadata.name -n consul

k.podnodns='kubectl get pod -o=custom-columns=NODE:.spec.nodeName,NAME:.metadata.name --namespace '
k.podstnod='kubectl get pod -o=custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName --all-namespaces'

kubectl get po -n apps -l 'team=customer-retention'

helm ls --all --short | xargs -L1 | grep -e "product-search"
helm ls --all --short --filter "product-search"

kubectl -n argocd port-forward svc/argocd-server -n argocd 8080:443
kubectl -n apps port-forward svc/kuberhealthy 8080:80

k get pods --selector k8s-app=aws-node-termination-handler -o=custom-columns=NODE:.spec.nodeName,NAME:.metadata.name
kubectl get nodes --selector='eks-managed=true'
kubectl get nodes --selector='eks-self-managed=true'
kubectl get nodes --selector='iam/scope=namespace'

kubectl get nodes --selector='group-name=spot-worker-group1-1.22'
kubectl get nodes --selector='group-name=apm-enabled-spot-worker-group1-1.22'
kubectl get nodes --selector='group-name=spot-worker-group1-ns-1.22'
kubectl get nodes --selector='group-name=ondemand-airflow-group1-1.22'
# done
kubectl get nodes --selector='group-name=ondemand-cluster-resources-group1-1.22'

kubectl get nodes --selector='group-name=spot-worker-group2-1.22'
kubectl get nodes --selector='group-name=spot-worker-group2-ns-1.22'
kubectl get nodes --selector='group-name=apm-enabled-spot-worker-group2-1.22'
kubectl get nodes --selector='group-name=apm-enabled-spot-worker-group2-ns-1.22'
kubectl get nodes --selector='group-name=ondemand-cluster-resources-group2-1.22'


kubectl get pod --selector app=ik-callback-app -o yaml | k neat

k get nodes --selector group-name=apm-enabled-spot-worker-group2-1.22

kubectl run mycurlpod --image=curlimages/curl -i --tty -- sh
kubectl run mycurlpod --image=dwdraju/alpine-curl-jq -i --tty -- sh

# get all pods with error image pull
kubectl get pods | grep "Image" | grep "$team"
# to retrieve an image
kubectl get pod $pod-name -o jsonpath='{..image}' | awk '{print $1}'

# show all unigue teams deployed on the cluster
kubectl get pods -o jsonpath='{..labels.team}' | tr -s '[[:space:]]' '\n' | sort | uniq
# show all pods with label team
k get pods -L team
# show specific columns
k get pods -o=custom-columns=NAME:.metadata.name,Namespace:.metadata.labels.team
# service with specific columns
kubectl get svc -o=custom-columns=NAME:.metadata.name,IP:.spec.clusterIP,PORT:.spec.ports[*].targetPort
# burstable pods
kubectl get pods --namespace apps --output=custom-columns=NAME:.metadata.name,NAMESPACE:.metadata.namespace,QOS-CLASS:.status.qosClass | grep Burstable

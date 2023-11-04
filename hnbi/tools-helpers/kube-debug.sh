#!/bin/bash

# should be somewhere equal a number of nodes
kubectl -n datadog get daemonset

kubectl get nodes --no-headers | wc -l

kubectl get nodes -o json | jq '.items[].spec'

#

#  https://www.bluematador.com/learn/kubectl-cheatsheet
#  https://learnk8s.io/

# How do you find all non-running pods (i.e., with a state other than Running)?
kubectl get pods -A --field-selector=status.phase!=Running | grep -v Complete

# Here is how you can get the list of nodes and their memory size:

kubectl get no -o json | \
  jq -r '.items | sort_by(.status.capacity.memory)[]|[.metadata.name,.status.capacity.memory]| @tsv'

#  Getting the list of nodes and the number of pods running on them

kubectl get po -o json --all-namespaces | \
  jq '.items | group_by(.spec.nodeName) | map({"nodeName": .[0].spec.nodeName, "count": length}) | sort_by(.count)'

# Sometimes, DaemonSet does not schedule a pod on a node for whatever reason.

ns=datadog
pod_template=my-pod
kubectl get node | grep -v \"$(kubectl -n ${ns} get pod --all-namespaces -o wide | fgrep ${pod_template} | awk '{print $8}' | xargs -n 1 echo -n "\|" | sed 's/[[:space:]]*//g')\"

# cpu
kubectl top pods -A | sort --reverse --key 3 --numeric
# memory
kubectl top pods -A | sort --reverse --key 4 --numeric
# Sorting the list of pods (in this case, by the number of restarts)
kubectl get pods --sort-by=.status.containerStatuses[0].restartCount
# Here is how you can easily print limits and requests of each pod
kubectl get pods -n my-namespace -o=custom-columns='NAME:spec.containers[*].name,MEMREQ:spec.containers[*].resources.requests.memory,MEMLIM:spec.containers[*].resources.limits.memory,CPUREQ:spec.containers[*].resources.requests.cpu,CPULIM:spec.containers[*].resources.limits.cpu'

# Networking

# Here is how you can get internal IP addresses of cluster nodes
kubectl get nodes -o json | \
  jq -r '.items[].status.addresses[]? | select (.type == "InternalIP") | .address' | \
  paste -sd "\n" -
# And this way, you can print all services and their respective nodePorts
kubectl get --all-namespaces svc -o json | \
  jq -r '.items[] | [.metadata.name,([.spec.ports[].nodePort | tostring ] | join("|"))]| @tsv'

# Secrets
# Here is how you can quickly copy secrets from one namespace to another:
kubectl get secrets -o json --namespace namespace-old | \
  jq '.items[].metadata.namespace = "namespace-new"' | \
  kubectl create-f  -

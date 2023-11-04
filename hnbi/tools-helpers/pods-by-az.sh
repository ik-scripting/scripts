#!/bin/bash

# Define the label selector
selector="app=calvin-hello-world"

# Get the list of nodes where the pods are running
nodes=$(kubectl get pods -l $selector -o wide | grep -v NODE | awk '{print $7}')

# Loop through the list of nodes and get their AZ labels
for node in $nodes
do
  kubectl get node $node --show-labels | grep -v NAME | cut -d',' -f19
done | sort | uniq -c


# beta.kubernetes.io/arch=amd64
# beta.kubernetes.io/instance-type=t3.large
# beta.kubernetes.io/os=linux
# datadog-agent=standard
# dedicated=worker
# eks-self-managed=true
# failure-domain.beta.kubernetes.io/region=eu-west-1
# failure-domain.beta.kubernetes.io/zone=eu-west-1a
# group-name=spot-worker-group2-1.23
# iam/scope=instance
# k8s.io/cloud-provider-aws=7c6056c6a76a2e253c3954c7c54156ac
# kubernetes.io/arch=amd64
# kubernetes.io/hostname=ip-10-1-161-228.eu-west-1.compute.internal
# kubernetes.io/os=linux
# node.kubernetes.io/instance-type=t3.large
# node.kubernetes.io/lifecycle=spot
# team=paas
# topology.kubernetes.io/region=eu-west-1
# topology.kubernetes.io/zone=eu-west-1a <-- 19th
# vpc.amazonaws.com/eniConfig=eu-west-1a

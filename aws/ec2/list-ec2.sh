#!/usr/bin/env bash

aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=gitlab-runner" \
  "Name=instance-state-name,Values=running" \
  |  jq -r ".Reservations[] | .Instances[*] | .[InstanceId,InstanceType,Tags]"

aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=gitlab-runner" \
  "Name=instance-state-name,Values=running" \
  --query "Reservations[*].Instances[*]"
# gitlab runners
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=gitlab-runner" \
  "Name=instance-state-name,Values=running" \
  --query "Reservations[*].Instances[*].{Type:InstanceType,LaunchTime:LaunchTime,NameTag:Tags[?Key=='Name'].Value,OwnerTag:Tags[?Key=='Owner'].Value}" \
  | jq -r .
# eks ci runners
aws ec2 describe-instances \
  --filters "Name=tag:karpenter.sh/provisioner-name,Values=cluster-resources-blue" \
  "Name=instance-state-name,Values=running" \
  --query "Reservations[*].Instances[*].{Type:InstanceType,LaunchTime:LaunchTime,NameTag:Tags[?Key=='Name'].Value,\"TAG-managed-by\":Tags[?Key=='karpenter.sh/managed-by'],\"TAG-provisioner-name\":Tags[?Key=='karpenter.sh/provisioner-name']}" | jq -r .


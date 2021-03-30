#!/usr/bin/env bash

set -e

export AWS_ACCESS_KEY_ID=""
export AWS_SECRET_ACCESS_KEY=""
export AWS_DEFAULT_REGION="eu-west-1"
# wget http://stedolan.github.io/jq/download/linux64/jq
asg=$(aws autoscaling describe-auto-scaling-groups --auto-scaling-group-name pista-test-genymotion \
|  jq -r '.AutoScalingGroups[] | select(.Tags[].Value="pista-test-genymotion").AutoScalingGroupARN')

sg=$(aws ec2 describe-security-groups \
--filters "Name=tag:Owner,Values=api.development@hermes-europe.co.uk" \
"Name=tag:Name,Values=pista-test-genymotion" \
|  jq -r '.SecurityGroups[] | .GroupId')

if [ -z "$asg" ];then
    echo Could not find autoscaling group
    exit 1
fi
if [ -z "$sg" ];then
    echo Could not find security group
    exit 1
fi

echo "Autoscaling Group ${asg}"
echo "Security Group ${sg}"

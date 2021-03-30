#!/usr/bin/env bash

export AWS_ACCESS_KEY_ID=""
export AWS_SECRET_ACCESS_KEY=""
export AWS_DEFAULT_REGION="eu-west-1"
# wget http://stedolan.github.io/jq/download/linux64/jq
ipaddress=$(aws ec2 describe-instances \
--filters "Name=instance-type,Values=t2.small" \
"Name=instance-state-name,Values=running" \
"Name=tag:Owner,Values=api.development@hermes-europe.co.uk" \
"Name=tag:Name,Values=pista-test-genymotion" \
|  jq -r ".Reservations[] | .Instances[] | .PrivateIpAddress")

if [ -z "$ipaddress" ];then
    echo Could not find the ip address
    exit 1
fi

echo "IP Address ${ipaddress}"
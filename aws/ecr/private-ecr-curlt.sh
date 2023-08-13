#!/bin/bash

# Access private ECR repository from list with curl
# Amazon private AWS ECRs https://docs.aws.amazon.com/eks/latest/userguide/add-ons-images.html

# only for username AWS
USER="AWS"
AWS_PWD=$(aws ecr get-login-password --region eu-west-1)
BASIC_AUTH=$(echo "$USER:$AWS_PWD" | base64 | tr -d "\n")
curl -H "Authorization: Basic $BASIC_AUTH" https://602401143452.dkr.ecr.eu-west-1.amazonaws.com/v2/eks/coredns/tags/list | jq

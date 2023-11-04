#!/bin/bash

kubectl describe pod aws-node-b76jp | grep IP | awk '{print $2}'

aws ec2 terminate-instances --instance-ids i-08900000000....

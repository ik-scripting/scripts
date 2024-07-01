#!/bin/bash

# This command will format the output in a table with columns for the Auto Scaling Group name, minimum size, maximum size, and desired capacity.
# This command uses the contains function in the JMESPath expression to filter ASG names that include group1 or group2 and returns their names
aws autoscaling describe-auto-scaling-groups --query 'AutoScalingGroups[?contains(AutoScalingGroupName, `group1`) || contains(AutoScalingGroupName, `group2`)].{Name:AutoScalingGroupName,MinSize:MinSize,MaxSize:MaxSize,DesiredCapacity:DesiredCapacity}' --output table

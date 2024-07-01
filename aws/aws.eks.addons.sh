#!/bin/bash
# https://www.dba-ninja.com/2022/09/aws-cli-cheatsheet.html

aws eks describe-addon-versions --kubernetes-version "1.27" --addon-name kube-proxy --query 'addons[].addonVersions[].{AddonVersion:addonVersion, ClusterVersion:compatibilities[0].clusterVersion, DefaultVersion:compatibilities[0].defaultVersion}' --output table

# -------------------------------------------------------------
# |                   DescribeAddonVersions                   |
# +---------------------+------------------+------------------+
# |    AddonVersion     | ClusterVersion   | DefaultVersion   |
# +---------------------+------------------+------------------+
# |  v1.27.12-eksbuild.5|  1.27            |  False           |
# |  v1.27.12-eksbuild.2|  1.27            |  False           |
# |  v1.27.10-eksbuild.2|  1.27            |  False           |
# |  v1.27.8-eksbuild.4 |  1.27            |  False           |
# |  v1.27.8-eksbuild.1 |  1.27            |  False           |
# |  v1.27.6-eksbuild.2 |  1.27            |  True            |
# |  v1.27.4-eksbuild.2 |  1.27            |  False           |
# |  v1.27.3-eksbuild.2 |  1.27            |  False           |
# |  v1.27.3-eksbuild.1 |  1.27            |  False           |
# |  v1.27.1-eksbuild.1 |  1.27            |  False           |
# |  v1.26.15-eksbuild.5|  1.27            |  False           |
# |  v1.26.15-eksbuild.2|  1.27            |  False           |
# |  v1.26.13-eksbuild.2|  1.27            |  False           |
# |  v1.26.11-eksbuild.4|  1.27            |  False           |
# |  v1.26.11-eksbuild.1|  1.27            |  False           |
# |  v1.26.9-eksbuild.2 |  1.27            |  False           |
# |  v1.26.7-eksbuild.2 |  1.27            |  False           |
# |  v1.26.6-eksbuild.2 |  1.27            |  False           |
# |  v1.26.6-eksbuild.1 |  1.27            |  False           |
# |  v1.26.4-eksbuild.1 |  1.27            |  False           |
# |  v1.25.16-eksbuild.8|  1.27            |  False           |
# |  v1.25.16-eksbuild.5|  1.27            |  False           |
# |  v1.25.16-eksbuild.3|  1.27            |  False           |
# |  v1.25.16-eksbuild.2|  1.27            |  False           |
# |  v1.25.16-eksbuild.1|  1.27            |  False           |
# |  v1.25.15-eksbuild.2|  1.27            |  False           |
# |  v1.25.14-eksbuild.2|  1.27            |  False           |
# |  v1.25.11-eksbuild.2|  1.27            |  False           |
# |  v1.25.6-eksbuild.2 |  1.27            |  False           |
# +---------------------+------------------+------------------+

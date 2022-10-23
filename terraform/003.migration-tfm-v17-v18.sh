#!/bin/bash

terragrunt state pull > terraform.tfstate
# update common hcl
terragrunt init --reconfigure

terragrunt state mv 'module.eks.aws_iam_role.cluster[0]' 'module.eks.aws_iam_role.this[0]'
terragrunt plan -target 'module.eks.aws_iam_role.this[0]'
terragrunt apply

terragrunt plan -target 'module.eks.aws_security_group_rule.cluster["egress_nodes_443"]' \
  -target 'module.eks.aws_security_group_rule.cluster["egress_nodes_kubelet"]' \
  -target 'module.eks.aws_security_group_rule.cluster["ingress_nodes_443"]' \
  -target 'module.eks.aws_security_group_rule.node["egress_cluster_443"]' \
  -target 'module.eks.aws_security_group_rule.node["egress_https"]' \
  -target 'module.eks.aws_security_group_rule.node["egress_ntp_tcp"]' \
  -target 'module.eks.aws_security_group_rule.node["egress_ntp_udp"]' \
  -target 'module.eks.aws_security_group_rule.node["egress_self_coredns_tcp"]' \
  -target 'module.eks.aws_security_group_rule.node["egress_self_coredns_udp"]' \
  -target 'module.eks.aws_security_group_rule.node["ingress_cluster_443"]' \
  -target 'module.eks.aws_security_group_rule.node["ingress_cluster_kubelet"]' \
  -target 'module.eks.aws_security_group_rule.node["ingress_self_coredns_tcp"]' \
  -target 'module.eks.aws_security_group_rule.node["ingress_self_coredns_udp"]'

# next
terragrunt apply

# do one by one just in case
terragrunt state rm 'aws_security_group_rule.alb_to_workers["external_health"]'
terragrunt state rm 'aws_security_group_rule.alb_to_workers["external_web"]'
terragrunt state rm 'aws_security_group_rule.alb_to_workers["internal_health"]'
terragrunt state rm 'aws_security_group_rule.alb_to_workers["internal_web"]'
terragrunt state rm 'aws_security_group_rule.eks_workers_additional["datadog-agent"]'
terragrunt state rm 'aws_security_group_rule.eks_workers_additional["vpn-ssh"]'

terragrunt plan -target 'aws_security_group_rule.alb_to_workers["external_health"]' \
 -target 'aws_security_group_rule.alb_to_workers["external_web"]' \
 -target 'aws_security_group_rule.alb_to_workers["internal_health"]' \
 -target 'aws_security_group_rule.alb_to_workers["internal_web"]' \
 -target 'aws_security_group_rule.eks_workers_additional["datadog-agent"]' \
 -target 'aws_security_group_rule.eks_workers_additional["vpn-ssh"]'

# TODO: remove it manually after migration to eks 1.21
terragrunt state rm 'module.eks.aws_security_group.workers[0]'
terragrunt state rm 'module.eks.aws_security_group_rule.workers_ingress_self[0]'
terragrunt state rm 'module.eks.aws_security_group_rule.workers_ingress_cluster_https[0]'
terragrunt state rm 'module.eks.aws_security_group_rule.workers_ingress_cluster[0]'
terragrunt state rm 'module.eks.aws_security_group_rule.workers_egress_internet[0]'
terragrunt state rm 'module.eks.aws_security_group_rule.cluster_https_worker_ingress[0]'
terragrunt state rm 'module.eks.aws_security_group_rule.cluster_egress_internet[0]'

# TODO: remove it manually after migration to eks 1.21
terragrunt state rm 'module.eks.aws_iam_role.workers[0]'
terragrunt state rm 'module.eks.aws_iam_role_policy_attachment.workers_AmazonEKS_CNI_Policy[0]'
terragrunt state rm 'module.eks.aws_iam_role_policy_attachment.workers_AmazonEKSWorkerNodePolicy[0]'
terragrunt state rm 'module.eks.aws_iam_role_policy_attachment.workers_AmazonEC2ContainerRegistryReadOnly[0]'

terragrunt plan -target 'module.eks.aws_eks_cluster.this[0]'

# TODO investigate why/where its attached
terragrunt state rm 'module.eks.aws_iam_policy.cluster_deny_log_group[0]'
terragrunt state rm 'module.eks.aws_iam_policy.cluster_elb_sl_role_creation[0]'

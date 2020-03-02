#!/bin/bash
# SSH connection to jumpbox

set -euo pipefail

: $jumpip

./bin/pull-compute-resources.sh

set +a
source ./data/resources
set -a

cat > "./data/ssh-config.conf" <<EOF
Host bastion
  Hostname ${BASTION_IP}
  StrictHostKeyChecking no
  ControlMaster auto
  ControlPersist 5m

Host  ${MASTER_IPS} ${WORKER_IPS}
  ProxyCommand ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -W %h:%p k8s@bastion
EOF

ssh -F ./data/ssh-config.conf ${jumpip} -i ./data/cust_id_rsa -v

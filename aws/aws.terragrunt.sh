#!/bin/bash

set -euo pipefail
set +x

folder=${1:-NOT_SET}
command=${2:-plan}

cd "${folder}"
terragrunt "${command}"

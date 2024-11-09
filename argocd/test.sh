#!/usr/bin/env bash

export EVAL_DEBUG="echo" # override `eval` with `echo` to print the command


wrapper_bin=${WRAPPER_PATH:-$(dirname $0)/../bin/helm-wrapper.sh}


${wrapper_bin} template
${wrapper_bin} template -f values.yaml
${wrapper_bin} template -f secrets.yaml -f values.yaml
${wrapper_bin} template -f secrets.yaml -f secrets-global.yaml
${wrapper_bin} template -f secrets.yaml --values secrets-global.yaml -n secrets.yaml
${wrapper_bin} template --values values.yaml --values secrets-us-east-1.yaml --values secrets-49f3a3236d3b.yaml
${wrapper_bin} template --values values.yaml --values ../../secrets-global.yaml --values ../secrets-us-east-1.yaml --values secrets-49f3a3236d3b.yaml
# ${wrapper_bin} template -f secrets.yaml,secrets-global.yaml -n secrets.yaml # @todo: try to solve this only if we have to

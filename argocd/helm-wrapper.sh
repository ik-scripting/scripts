#!/usr/bin/env bash

export SOPS_FAILURES=$(mktemp)

function prepend() {

    while read line; do
        echo "${1}${line}"
    done
}

function sops_decrypt() {

    ENCRYPTED_FILE_PATH=$1

    # redirect stderr to a file so that we can track failures - we have no other way of capturing SOPS decryption failures
    sops -d ${ENCRYPTED_FILE_PATH} 2> >(prepend "${ENCRYPTED_FILE_PATH}: " | tee -a ${SOPS_FAILURES} >&2)
}

# set HELM_PATH to a custom helm location when e.g. testing locally
helm_bin=${HELM_PATH:-/usr/local/bin/_helm}

# set EVAL_DEBUG to a command to be used instead of eval (e.g. `echo` for testing)
eval_cmd=${EVAL_DEBUG:-eval}

# the original args to the `helm` command as a string
helm_args="$@"

# replace `--values secrets*.yaml` with `--values <(sops -d secrets*.yaml)`
# the <( ... ) ("process substitution") creates a temporary anonymous pipe to make helm read the output of the sops command
transformed_helm_args=$(echo ${helm_args} | sed -E 's/(-f|--values) ([^[:space:]]*secrets[^[:space:]]*.yaml)/\1 <(sops_decrypt \2)/g')

# execute the result
${eval_cmd} "${helm_bin} ${transformed_helm_args}"

EXIT_CODE=$?

if [ -s ${SOPS_FAILURES} ]; then
    EXIT_CODE=1
fi

rm ${SOPS_FAILURES} || true

exit ${EXIT_CODE}

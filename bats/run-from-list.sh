#!/usr/bin/env bash

set -e pipefail

: "${WORKSPACE}"
: "${TESTS_TO_RUN}"

cd "${WORKSPACE}"

while IFS= read -r test
do
  if [ "${#test}" -gt 0 ]; then
    echo "RUN: ${test}"
    bats --tap ${test};
    echo -e "done with: ${test} \n"
  fi
done << END
${TESTS_TO_RUN}
END

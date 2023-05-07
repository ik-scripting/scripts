#!/bin/bash

if [[ $# -lt 3 ]]; then
  echo "usage: $0 <file> <url> <checksum(s)...>" 1>&2
  exit 1
fi

set -xeou pipefail

FILE="$1"
URL="$2"
shift 2

curl --retry 6 -fsSL "$URL" -o "$FILE"

for checksum; do
  if echo "${checksum}  ${FILE}" | sha256sum -c -; then
    exit 0
  fi
done

exit 1

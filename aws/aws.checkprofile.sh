#!/bin/bash

# Check whether or not profile is set correctly

set -euo pipefail
: $AWS_PROFILE

if [ -z "${AWS_PROFILE:-}" ]; then
  echo "AWS_PROFILE not set."
  exit 1
fi

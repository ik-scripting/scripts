#!/bin/bash
# https://gitlab.com/gitlab-org/gitlab-build-images/-/blob/master/scripts/generate-locale
set -xeou pipefail

BUILD_OS=${BUILD_OS:-debian}

# For UBI, the locale is already present in the image.
if [[ $BUILD_OS =~ debian ]]; then
    locale-gen C.UTF-8
fi

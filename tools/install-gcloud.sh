# https://gitlab.com/gitlab-org/gitlab-build-images/-/blob/master/scripts/install-gcloud
#!/bin/bash

set -xeuo pipefail

GCLOUD_VERSION=${1}

function build_debian() {
    export DEBIAN_FRONTEND=noninteractive
    apt-get update
    apt-get -y install \
        apt-transport-https \
        python3 \
        gnupg

    curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
    echo "deb https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

    apt-get update

    PACKAGE_VERSION=$(apt-cache policy google-cloud-cli | awk -v dv=${GCLOUD_VERSION} '$1 ~ dv {print $1}')

    apt-get install -y google-cloud-cli=${PACKAGE_VERSION}
    apt-get -yq autoremove
    apt-get clean -yqq
    rm -rf /var/lib/apt/lists/*
}

BUILD_OS=${BUILD_OS:-debian}

if [[ $BUILD_OS =~ debian ]]; then
    build_debian "$@"
elif [[ $BUILD_OS =~ ubi ]]; then
    build_ubi "$@"
fi

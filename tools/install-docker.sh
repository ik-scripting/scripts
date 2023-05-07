# https://gitlab.com/gitlab-org/gitlab-build-images/-/blob/master/scripts/install-docker
#!/bin/bash

set -xeuo pipefail

export DEBIAN_FRONTEND=noninteractive

DOCKER_VERSION=${1}
DEBIAN_VERSION=$(lsb_release -c -s)

apt-get update && apt-get -y install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg

mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  ${DEBIAN_VERSION} stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update

PACKAGE_VERSION=$(apt-cache policy docker-ce | awk -v dv=${DOCKER_VERSION} '$1 ~ dv {print $1}')

 apt-get install -y \
    docker-ce=${PACKAGE_VERSION} \
    docker-ce-cli=${PACKAGE_VERSION} \
    docker-buildx-plugin

apt-get -yq autoremove
apt-get clean -yqq
rm -rf /var/lib/apt/lists/*

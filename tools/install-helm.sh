# https://gitlab.com/gitlab-org/gitlab-build-images/-/blob/master/scripts/install-helm
#!/bin/bash

set -xeou pipefail

HELM_VERSION=${1}
HELM_DOWNLOAD_SHA256=${2}
HELM_DOWNLOAD_URL="https://get.helm.sh/helm-v${HELM_VERSION}-linux-${TARGETARCH:-amd64}.tar.gz"

/scripts/download-file helm.tar.gz "$HELM_DOWNLOAD_URL" $HELM_DOWNLOAD_SHA256

tar -xzf helm.tar.gz --strip-components=1
rm helm.tar.gz

chmod +x helm
mv helm /usr/bin/

helm version --client

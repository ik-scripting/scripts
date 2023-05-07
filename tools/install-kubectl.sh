# https://gitlab.com/gitlab-org/gitlab-build-images/-/blob/master/scripts/install-kubectl
#!/bin/bash

set -xeou pipefail

KUBECTL_VERSION=${1}
KUBECTL_DOWNLOAD_SHA256=${2}
KUBECTL_DOWNLOAD_URL="https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/${TARGETARCH:-amd64}/kubectl"

/scripts/download-file kubectl "$KUBECTL_DOWNLOAD_URL" $KUBECTL_DOWNLOAD_SHA256

chmod +x kubectl
mv kubectl /usr/local/bin/kubectl

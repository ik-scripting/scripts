# https://gitlab.com/gitlab-org/gitlab-build-images/-/blob/master/scripts/install-node
#!/bin/bash
set -xeuo pipefail
IFS=$'\n\t'

NODE_INSTALL_VERSION=${1}
YARN_INSTALL_VERSION=${2}

# Map MAJOR.MINOR.patch -> MAJOR.x
NODE_MAJOR=$(echo "$NODE_INSTALL_VERSION" | sed -r -e "s/([0-9]+)\.[0-9]+.*/\1\.x/g")

# add official debian repos for node
curl -sS -L "https://deb.nodesource.com/setup_${NODE_MAJOR}" | bash -

apt-get update

NODE_FILE_NAME="nodejs_$NODE_INSTALL_VERSION-deb-1nodesource1_${TARGETARCH:-amd64}.deb"
curl -s -O "https://deb.nodesource.com/node_$NODE_MAJOR/pool/main/n/nodejs/$NODE_FILE_NAME"
dpkg -i "$NODE_FILE_NAME"
rm -f "$NODE_FILE_NAME"

npm install --global "yarn@${YARN_INSTALL_VERSION}"
npm cache clean --force

apt-get autoremove -yq
apt-get clean -yqq
rm -rf /var/lib/apt/lists/*

node --version
yarn --version

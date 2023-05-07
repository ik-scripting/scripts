# https://gitlab.com/gitlab-org/gitlab-build-images/-/blob/master/scripts/install-golang
#!/bin/bash

set -xeou pipefail

INSTALL_GOLANG_VERSION=${1}
GOLANG_DOWNLOAD_SHA256=${2}

GOLANG_DOWNLOAD_URL="https://golang.org/dl/go${INSTALL_GOLANG_VERSION}.linux-${TARGETARCH:-amd64}.tar.gz"

function build_debian() {
    /scripts/download-file golang.tar.gz "$GOLANG_DOWNLOAD_URL" $GOLANG_DOWNLOAD_SHA256
    tar -C /usr/local -xzf golang.tar.gz
    rm golang.tar.gz
}

function build_ubi() {
    GO_MAJOR_VERSION=${INSTALL_GOLANG_VERSION%.*}

    mkdir -p /tmp/golang
    curl -fsSL "$GOLANG_DOWNLOAD_URL" -o golang.tar.gz
    echo "${GOLANG_DOWNLOAD_SHA256}  golang.tar.gz" | sha256sum -c -
    tar -C /tmp/golang -xzf golang.tar.gz

    # For UBI, we will be installing golang-fips
    # Use a different build process when golang version is less-than-equal to 1.18
    if [[ $(echo -e "1.18\n${GO_MAJOR_VERSION}" | sort -V | tail -1) == '1.18' ]]; then
        git clone https://github.com/golang-fips/go.git --branch "go${GO_MAJOR_VERSION}-openssl-fips" --single-branch --depth 1 /usr/local/go

        cd /usr/local/go/src
        PATH=$PATH:/tmp/golang/go/bin CGO_ENABLED=1 ./make.bash
    else
        # This is a workaround until https://github.com/golang-fips/go/issues/82 is resolved.
        if [[ $GO_MAJOR_VERSION == "1.20" ]]; then
            GO_BRANCH="go1.20.3-openssl-fips"
        else
            GO_BRANCH="go${GO_MAJOR_VERSION}-fips-release"
        fi

        git clone https://github.com/golang-fips/go.git --branch "${GO_BRANCH}" --single-branch --depth 1 /tmp/golang-fips
        cd /tmp/golang-fips

        # The initialize script ends with a commit, so we need to set the user info. And needs to be global due to submodules in use.
        git config --global user.email "builder@example.com"
        git config --global user.name "Builder"

        PATH=$PATH:/tmp/golang/go/bin ./scripts/full-initialize-repo.sh

        cd /tmp/golang-fips/go/src
        PATH=$PATH:/tmp/golang/go/bin GOROOT_FINAL=/usr/local/go CGO_ENABLED=1 ./make.bash
        mv /tmp/golang-fips/go /usr/local/go
    fi

    rm -rf /usr/local/go/pkg/*/cmd /usr/local/go/pkg/bootstrap \
          /usr/local/go/pkg/obj /usr/local/go/pkg/tool/*/api \
          /usr/local/go/pkg/tool/*/go_bootstrap /usr/local/go/src/cmd/dist/dist \
          /usr/local/go/.git* /tmp/golang /tmp/golang-fips

    ln -sf /usr/local/go/bin/go /usr/local/go/bin/gofmt /usr/local/go/bin/godoc /usr/local/bin/
}


BUILD_OS=${BUILD_OS:-debian}

if [[ $BUILD_OS =~ debian ]]; then
    build_debian "$@"
elif [[ $BUILD_OS =~ ubi ]]; then
    build_ubi "$@"
fi

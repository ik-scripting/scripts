# https://gitlab.com/gitlab-org/gitlab-build-images/-/blob/master/scripts/install-chrome
#!/bin/bash

set -xeuo pipefail
IFS=$'\n\t'

function download_noto() {
    local NOTO_VERSION
    # https://github.com/googlefonts/noto-emoji/releases/tag/v2.038
    NOTO_VERSION="v2.038"
    curl --silent -O --location --fail "https://github.com/googlefonts/noto-emoji/raw/${NOTO_VERSION}/fonts/NotoColorEmoji.ttf"
    echo "NotoColorEmoji.ttf"
}

function download_deb() {
    local COMPONENT=$1
    local VERSION=$([ "${ARCH}" == "amd64" ] && echo "$CHROME_VERSION" || echo "$CHROMIUM_VERSION")
    local DEB=$([ "${COMPONENT}" == "browser" ] && echo "${PKG}_${VERSION}_${ARCH}.deb" || echo "${PKG}-${COMPONENT}_${VERSION}_${ARCH}.deb")

    curl --silent --show-error --fail -O "${DOWNLOAD_URL_BASE}/${VERSION}/${DEB}"
    echo "${DEB}"
}

function build_debian() {
    apt-get update

    echo "Installing browser"
    BROWSER_DEB="$(download_deb browser)"
    if [ "${ARCH}" == "arm64" ]; then
        COMMON_DEB=$(download_deb common)
        apt-get install -y "./${COMMON_DEB}" "./${BROWSER_DEB}"
        rm -rf "$COMMON_DEB"
    else
        apt-get install -y "./${BROWSER_DEB}"
    fi
    rm -f "$BROWSER_DEB"

    echo "Installing webdriver"
    if [ "${ARCH}" == "amd64" ]; then
        CHROME_VERSION_BASE=$(echo $CHROME_VERSION | awk -F "." '{print $1 "." $2 "." $3}')
        CHROME_DRIVER_VERSION=$(curl -q https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION_BASE)

        wget -q https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip
        unzip chromedriver_linux64.zip -d /usr/local/bin
        rm -f chromedriver_linux64.zip
    else
        DRIVER_DEB=$(download_deb driver)
        apt-get install -y "./$DRIVER_DEB"
        rm -f "$DRIVER_DEB"
    fi

    # We have loads of tests rendering emoji, so let's ensure a proper emoji font is installed
    echo "Installing Noto emoji font"
    FONT_FILE=$(download_noto)

    mkdir -p /usr/local/share/fonts
    mv "$FONT_FILE" /usr/local/share/fonts/
    chmod 644 "/usr/local/share/fonts/${FONT_FILE}"
    ls -la /usr/local/share/fonts/

    fc-cache -fv
    fc-match -s noto

    # Cleanup
    apt-get autoremove -yq
    apt-get clean -yqq
    rm -rf /var/lib/apt/lists/*
    rm -rf /etc/apt/sources.list.d/google*.list
}

function build_ubi() {
    echo "This OS is not supported for chrome install!"
    exit 1
}

BUILD_OS=${BUILD_OS:-debian}
OS_VERSION=${OS_VERSION:-bullseye}
CHROME_VERSION=${1:-111.0.5563.64-1}
CHROMIUM_VERSION=${2:-$CHROME_VERSION}
ARCH=${TARGETARCH:-amd64}
PKG=$([ "${ARCH}" == "amd64" ] && echo "google-chrome-stable" || echo "chromium")
DOWNLOAD_URL_BASE="https://gitlab.com/api/v4/projects/1075790/packages/generic/${BUILD_OS}-${OS_VERSION}-${PKG}"

if [[ $BUILD_OS =~ debian ]]; then
    build_debian "$@"
elif [[ $BUILD_OS =~ ubi ]]; then
    build_ubi "$@"
fi

if [ "${ARCH}" == "amd64" ]; then
    google-chrome --version
else
    chromium --version
fi

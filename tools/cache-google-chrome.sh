#!/bin/bash
# https://gitlab.com/gitlab-org/gitlab-build-images/-/blob/master/scripts/cache-google-chrome
# This script attempts to copy the latest version of the Google Chrome Debian
# package into our own package registry. Google yanks old versions regularly,
# making it hard to keep up with all the new versions.

set -e

export DEBIAN_FRONTEND=noninteractive

function save-package() {
  local PKG=$1
  local DEB=$2
  local LATEST_VERSION=$3
  local REGISTRY_PACKAGE=${4:-$PKG}
  local SOURCE_DEB=${5:-$DEB}

  local URL="${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages/generic/${BUILD_OS}-${OS_VERSION}-${REGISTRY_PACKAGE}/${LATEST_VERSION}/${DEB}"

  echo "Checking if ${PKG} v${LATEST_VERSION} is already cached"
  local FILE_CHECK=$(curl --silent --location --head --output /dev/null --write "%{http_code}\\n" "$URL")

  if [ "$FILE_CHECK" -eq "200" ]; then
    echo "${PKG} v${LATEST_VERSION} is already cached!"
  else
    echo "Downloading latest ${PKG} version (${LATEST_VERSION}) from apt repository..."
    cd /tmp
    apt-get download "$PKG"

    if ! [ -f "${SOURCE_DEB}" ]; then
      echo "Downloaded file didn't have expected name: ${SOURCE_DEB}"
      ls
      exit 1
    fi

    if [ "$SOURCE_DEB" != "$DEB" ]; then
      mv "$SOURCE_DEB" "$DEB"
    fi

    echo "Transferring ${PKG} v${LATEST_VERSION} to GitLab packages"
    curl --fail --header "JOB-TOKEN: ${CI_JOB_TOKEN}" \
      --upload-file "./{$DEB}" \
      "$URL"

    echo "$LATEST_VERSION" >chrome-version # save latest version to file to indicate a new version has been cached
  fi
}

function cache-chrome() {
  PKG=google-chrome-stable

  echo "Updating apt to get Google Chrome packages..."
  curl -sS -L https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
  echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >/etc/apt/sources.list.d/google.list
  apt-get -y -qq update

  echo "Checking for latest '${PKG}' version in apt repository..."
  LATEST_VERSION=$(apt-cache show $PKG | grep Version | sort | tail -1 | sed -e "s/Version: //")
  CHROME_DEB="google-chrome-stable_${LATEST_VERSION}_amd64.deb"

  save-package "$PKG" "$CHROME_DEB" "$LATEST_VERSION"
}

function cache-chromium() {
  PKG=chromium
  PKG_DRIVER=chromium-driver
  PKG_COMMON=chromium-common

  echo "Checking for latest '${PKG}' version in apt repository..."
  LATEST_VERSION=$(apt-cache show $PKG | grep Version | sort | tail -1 | sed -e "s/Version: //")
  VERSION_NUMBER=$(echo $LATEST_VERSION | sed -e "s/~deb.*//") # remove debian version part to have chrome and chromium compatible version numbers
  CHROMIUM_DEB="${PKG}_${VERSION_NUMBER}_${TARGETARCH}.deb"
  CHROMIUM_DRIVER_DEB="${PKG_DRIVER}_${VERSION_NUMBER}_${TARGETARCH}.deb"
  CHROMIUM_COMMON_DEB="${PKG_COMMON}_${VERSION_NUMBER}_${TARGETARCH}.deb"

  # Save chromium, chromium-common and chromium-driver under the same package
  save-package "$PKG" "$CHROMIUM_DEB" "$VERSION_NUMBER" "${PKG}" "${PKG}_${LATEST_VERSION}_${TARGETARCH}.deb"
  save-package "$PKG_DRIVER" "$CHROMIUM_DRIVER_DEB" "$VERSION_NUMBER" "${PKG}" "${PKG_DRIVER}_${LATEST_VERSION}_${TARGETARCH}.deb"
  save-package "$PKG_COMMON" "$CHROMIUM_COMMON_DEB" "$VERSION_NUMBER" "${PKG}" "${PKG_COMMON}_${LATEST_VERSION}_${TARGETARCH}.deb"
}

function notify-chrome-updated() {
  [ ! -f chrome-version ] && exit
  [ -z "$CI_SLACK_WEBHOOK_URL" ] && exit

  local chrome_version=$(cat chrome-version)
  local msg="New version of chrome has been released: \`${chrome_version}\`!\n"
  msg+="Consider updating versions in:\n"
  msg+="- https://gitlab.com/gitlab-org/gitlab-build-images\n"
  msg+="- https://gitlab.com/gitlab-org/gitlab"

  local payload="{\"text\":\"$msg\",\"channel\":\"#quality\",\"icon_emoji\":\":chrome:\",\"username\":\"chrome-update\"}"

  echo "Notifying #quality channel of new chrome version release!"
  curl -s -X POST -H 'Content-type: application/json' --data "$payload" "$CI_SLACK_WEBHOOK_URL"
}

echo "Updating system utils"
apt-get -y -qq update
apt-get -y install apt-utils curl gnupg2 >/dev/null

if [ "$TARGETARCH" == "amd64" ]; then
  cache-chrome
  cache-chromium
else
  cache-chromium
  [ "$NOTIFY_VERSION_UPDATE" == "true" ] && notify-chrome-updated || exit 0
fi

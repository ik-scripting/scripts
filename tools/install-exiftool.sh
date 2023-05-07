# https://gitlab.com/gitlab-org/gitlab-build-images/-/blob/master/scripts/install-exiftool
#!/bin/bash

set -xeuo pipefail

mkdir build \
  && curl -fsSL "$EXIFTOOL_DOWNLOAD_URL" -o exiftool.tar.gz \
  && echo "$EXIFTOOL_DOWNLOAD_SHA256 exiftool.tar.gz" | sha256sum -c - \
  && tar -C build -xzf exiftool.tar.gz

cd build/exiftool-$EXIFTOOL_VERSION

# Apply patches
patchdir="/patches/exiftool/${EXIFTOOL_VERSION}"
if [[ -d "${patchdir}" ]]; then
  for i in "${patchdir}"/*.patch; do
    echo "$i..."
    patch -p1 -i "$i"
  done
else
  echo "!! Missing exiftools patch"
  echo "!! Make sure the patch exists for exiftool version ${EXIFTOOL_VERSION} before proceeding."
  exit 1
fi

perl Makefile.PL \
  && make install \
  && cd ../.. \
  && rm -rf build \
  && rm exiftool.tar.gz

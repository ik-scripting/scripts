# https://gitlab.com/gitlab-org/gitlab-build-images/-/blob/master/scripts/install-ruby
#!/bin/bash

set -xeou pipefail

# Based on https://github.com/docker-library/ruby/blob/master/2.7/bullseye/Dockerfile

RUBY_VERSION=${1}
RUBY_MAJOR=${1%.*} # strip last component
RUBY_DOWNLOAD_SHA256=${2}
RUBY_DOWNLOAD_URL="https://cache.ruby-lang.org/pub/ruby/${RUBY_MAJOR%-rc}/ruby-$RUBY_VERSION.tar.gz"

JEMALLOC_VERSION=5.3.0
JEMALLOC_DOWNLOAD_SHA256="2db82d1e7119df3e71b7640219b6dfe84789bc0537983c3b7ac4f7189aecfeaa"
JEMALLOC_DOWNLOAD_URL="https://github.com/jemalloc/jemalloc/releases/download/${JEMALLOC_VERSION}/jemalloc-${JEMALLOC_VERSION}.tar.bz2"

BUNDLER_VERSION=${3:-""}
RUBYGEMS_VERSION=${4:-""}

function build_common() {
    # Download jemalloc
    mkdir -p /usr/src/jemalloc
    cd /usr/src/jemalloc
    curl --retry 6 -L -so jemalloc.tar.bz2 ${JEMALLOC_DOWNLOAD_URL}
    echo "${JEMALLOC_DOWNLOAD_SHA256} jemalloc.tar.bz2" | sha256sum -c -

    # Install jemalloc
    tar -xjf jemalloc.tar.bz2
    rm jemalloc.tar.bz2
    cd jemalloc-${JEMALLOC_VERSION}
    ./autogen.sh --prefix=/usr --enable-prof
    make -j "$(nproc)" install
    cd /tmp

    # Download Ruby
    curl -fsSL "$RUBY_DOWNLOAD_URL" -o ruby.tar.gz
    echo "${RUBY_DOWNLOAD_SHA256} ruby.tar.gz" | sha256sum -c -

    # Skip installing Gem docs
    mkdir -p /usr/local/etc
    echo 'install: --no-document' >> /usr/local/etc/gemrc
    echo 'update: --no-document' >> /usr/local/etc/gemrc

    # Unpack Ruby
    mkdir -p /usr/src/ruby
    tar -xzf ruby.tar.gz -C /usr/src/ruby --strip-components=1
    rm ruby.tar.gz
    cd /usr/src/ruby

    # Process patch files
    local ruby_version=$(cut -d '.' -f 1,2 <<< $RUBY_VERSION)
    local patchdir="/patches/ruby/${ruby_version}"

    # Verify mandatory patches
    while read -r patchname; do
      local patchfile="${patchdir}/${patchname}.patch"
      if [[ ! -f "${patchfile}" ]]; then
        echo "!! Missing mandatory patch ${patchname}"
        echo "!! Make sure ${patchfile} exists before proceeding."
        exit 1
      fi
    done < "/patches/ruby/mandatory_patches"

    # Apply patches
    if [[ -d "${patchdir}" ]]; then
      for i in "${patchdir}"/*.patch; do
        echo "$i..."
        patch -p1 -i "$i"
      done
    fi

    # Compile
    # This is needed for Ruby < 3.1 on Debian bullseye: https://bugs.ruby-lang.org/issues/18409
    export LDFLAGS="-Wl,--no-as-needed"
    cflags="-fno-omit-frame-pointer" ./configure --enable-shared --with-jemalloc --disable-install-doc --disable-install-rdoc --disable-install-capi
    make install -j $(nproc)

    # Install specific version of bundler if provided
    if [[ "$BUNDLER_VERSION" != "" ]]; then gem install bundler -v $BUNDLER_VERSION; fi

    # Install specific version of RubyGems if provided
    if [[ "$RUBYGEMS_VERSION" != "" ]]; then gem update --system $RUBYGEMS_VERSION; fi

    # Cleanup
    cd /
    rm -rf /usr/src/ruby /usr/src/jemalloc
}

function build_debian() {
    # Install needed packages
    apt-get update
    apt-get install -y --no-install-recommends bison dpkg-dev libgdbm-dev autoconf

    build_common

    apt-get purge -y --auto-remove ruby

    # Verify
    # verify we have no "ruby" packages installed
    ! dpkg -l | grep -i ruby
    [ "$(command -v ruby)" = '/usr/local/bin/ruby' ]
}

function build_ubi() {
    yum update -y

    build_common

    yum remove -y ruby
    yum autoremove -y
    yum clean -y all

    # Verify
    # verify we have no "ruby" packages installed
    ! yum list installed | grep -i ruby
    [ "$(command -v ruby)" = '/usr/local/bin/ruby' ]
}

BUILD_OS=${BUILD_OS:-debian}

if [[ $BUILD_OS =~ debian ]]; then
    build_debian "$@"
elif [[ $BUILD_OS =~ ubi ]]; then
    build_ubi "$@"
fi

# rough smoke test
ruby --version
gem --version
bundle --version

# https://gitlab.com/gitlab-org/gitlab-build-images/-/blob/master/scripts/install-essentials
#!/bin/bash

set -xeuo pipefail
IFS=$'\n\t'

# We install `git-core` as some tooling expect `/usr/bin/git`
# other tools that rely on PATH ordering will pick a one in `/usr/local`
# if present
function install_debian_bullseye_deps() {
    apt-get install -y \
            curl wget build-essential apt-utils clang locales openssh-client \
            libclang-dev libssl-dev libyaml-dev libreadline-dev llvm-dev zlib1g-dev \
            libncurses5-dev libffi-dev ca-certificates libxml2-dev \
            libxslt1-dev libcurl4-openssl-dev libicu-dev \
            logrotate python3-docutils pkg-config cmake \
            libkrb5-dev postgresql-client unzip \
            libsqlite3-dev libpq-dev libpng-dev libjpeg-dev libzstd-dev \
            libre2-dev libevent-dev gettext rsync git-core lsb-release
}

function prepare_debian_environment() {
    export DEBIAN_FRONTEND=noninteractive

    apt-get update

    VERSION=`cat /etc/issue | cut -d ' ' -f 3`

    case "$VERSION" in
        11)
            install_debian_bullseye_deps
        ;;
    esac

    # Set UTF-8
    # http://stackoverflow.com/a/3182519/2137281
    LOC=$'LC_ALL=C.UTF-8\nLANG=C.UTF-8'
    echo "$LOC" > /etc/environment
    cat /etc/environment
    echo "C.UTF-8 UTF-8" > /etc/locale.gen
    locale-gen
    dpkg-reconfigure locales -f noninteractive -p critical
    locale -a

    apt-get autoremove -yq
    apt-get clean -yqq
    rm -rf /var/lib/apt/lists/*
}

function prepare_ubi_environment() {
    yum update -y

    yum install -by --nodocs \
                autoconf clang-devel cmake gcc gcc-c++ make patch perl bzip2 \
                libedit ncurses uuid libarchive curl-devel \
                libicu-devel libyaml-devel libedit-devel libffi-devel libuuid-devel openssl-devel \
                ncurses-devel pcre2-devel zlib-devel libstdc++-static \
                libevent-devel redhat-lsb-core procps-ng

    yum autoremove -y
    yum clean -y all
}

if [[ $1 =~ debian ]]; then
    prepare_debian_environment "$@"
elif [[ $1 =~ ubi ]]; then
    prepare_ubi_environment "$@"
fi

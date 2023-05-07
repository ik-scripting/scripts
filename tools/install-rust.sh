# https://gitlab.com/gitlab-org/gitlab-build-images/-/blob/master/scripts/install-rust
#!/bin/bash

set -xeou pipefail

INSTALL_RUST_VERSION=${1}

case "$TARGETARCH" in
  "arm64")
    RUST_TARGET="aarch64-unknown-linux-gnu"
    ;;
  "amd64")
    RUST_TARGET="x86_64-unknown-linux-gnu"
    ;;
  *)
    echo "target architecture not supported"
    exit 1
    ;;
esac

RUST_DOWNLOAD_URL="https://static.rust-lang.org/rustup/dist/$RUST_TARGET/rustup-init"

RUSTUP_DEFAULT_TOOLCHAIN="$INSTALL_RUST_VERSION"

export RUSTUP_HOME="/opt/rust"
export CARGO_HOME="/opt/rust"

function build() {
    curl --retry 3 --proto '=https' --tlsv1.2 -sSf "$RUST_DOWNLOAD_URL" > rustup-init
    curl --retry 3 --proto '=https' --tlsv1.2 -sSf "$RUST_DOWNLOAD_URL.sha256" > rustup-init.sha256
    # Remove "target/$RUST_TARGET/release/" string from rustup-init.sha256
    sed -i "s:\*target/$RUST_TARGET/release/::" rustup-init.sha256
    sha256sum -c rustup-init.sha256
    chmod +x rustup-init

    # Need rustfmt for bindgen doc parsing
    ./rustup-init --no-modify-path --default-toolchain "$RUSTUP_DEFAULT_TOOLCHAIN" --profile minimal --component rustfmt -y
    rm rustup-init && rm rustup-init.sha256

    chmod -R a+w "$RUSTUP_HOME" "$CARGO_HOME"

    # https://github.com/rust-lang/rustup/issues/1085
    cat <<EOF > /usr/local/bin/rust-wrapper
#!/bin/sh

RUSTUP_HOME=/opt/rust exec /opt/rust/bin/\${0##*/} "\$@"
EOF
    chmod +x /usr/local/bin/rust-wrapper

    for bin in /opt/rust/bin/*
    do
	ln -sf /usr/local/bin/rust-wrapper /usr/local/bin/$(basename $bin)
    done
}

build "$@"

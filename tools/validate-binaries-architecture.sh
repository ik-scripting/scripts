# https://gitlab.com/gitlab-org/gitlab-build-images/-/blob/master/scripts/validate-binaries-architecture
#!/bin/bash

set -eo pipefail

# convert architecture of a system into
# - use `arch` to show current system architecture
# - do not use `uname -m` as this shows kernel architecture
# - the `arch != uname -m` will be different when doing cross-compilation using `qemu-user`
# x86_64 -> x86-64
# aarch64 -> aarch64
ARCH=$(arch | tr '_' '-')

# find all executables in $PATH
CMDs=$(compgen -c)
CMD_PATHs=$(which $CMDs || true) # some CMDs might be missing

if files=$(file $CMD_PATHs | grep "ELF " | grep -v "$ARCH")
then
  echo "Found files of different architecture than $(ARCH):"
  echo "$files"
  exit 1
fi

echo "Validated $(echo $CMD_PATHs | wc -w) binaries."

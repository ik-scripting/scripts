#!/bin/bash

# Rotating data keys is also trivial: sops provides a rotation flag "-r"
# that will generate a new data key Kd and re-encrypt all values in the file with it.
#  Coupled with in-place encryption/decryption, it is easy to rotate all the keys on a group of files:

set -e

for file in $(find . -type f -name "*.yaml"); do
        sops -d -i $file
        sops -e -i -r $file
done

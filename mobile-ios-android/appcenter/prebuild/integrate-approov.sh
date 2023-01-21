#!/usr/bin/env bash

curl -O https://approov.io/downloads/approovcli.zip
unzip approovcli.zip
rm -rf approovcli.zip

mv approovcli/MacOS/approov /usr/local/bin/approov
rm -rf approovcli

echo "$HB_APPROOV_MANAGEMENT_TOKEN" > approov.tok
approov init approov.tok

npx @approov/react-native-approov integrate --no-prompt --init.prefetch true

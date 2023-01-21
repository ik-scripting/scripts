#!/bin/bash

set -eu

help() {
  echo "-----------------------------------------------------------------------"
  echo "                      Available commands                              -"
  echo "-----------------------------------------------------------------------"
  echo "   > build - To build the Docker image"
  echo "   > npm - To install NPM modules/deps"
  echo "   > bower - To install Bower/Js deps"
}

log() {
	echo -e "$1"
}

print_env() {
  [[ "$@" ]] && echo "options: $@"
  env
}

prepare_signature() {
  # secret encoded locally with command 'gpg -c --armor stampsapp.jks'
  mv ../secrets/certs .
  gpg -d --passphrase "${GPG_PASSPHRASE}" --batch certs/${ENVIRONMENT}/stampsapp.jks.asc > ${ANDROID_RELEASE_CERTIFICATE}
  cp ${ANDROID_RELEASE_CERTIFICATE} app/${ANDROID_RELEASE_CERTIFICATE}
}

prod_decrypt_certificate() {
  cd ../../cert
  gpg -d -q --passphrase "${MATCH_PASSWORD}" --batch stampsapp.jks.asc > "stampsapp.jks"
  echo -n "$PWD/stampsapp.jks"
}

cleanup() {
  rm "$1"
}

verify_signature() {
  signature=$(keytool -printcert -jarfile ${ARTIFACT_REGEX} | grep "SHA256:" -m 1 | head -1)
  certOwner=$(keytool -printcert -jarfile ${ARTIFACT_REGEX} | grep "Owner:" -m 1 | head -1)
  if [[ $signature =~ "${SIGNATURE_SHA256}" ]]; then
    echo -n "Certificate $certOwner"
  else
    echo "$certOwner: $signature ❌"
    exit 1
  fi
}

case $1 in
    help) "$@"; exit;;
    print_env) "$@"; exit;;
    git_token) "$@"; exit;;
    prepare_signature) "$@"; exit;;
    verify_signature) "$@"; exit;;
    prod_decrypt_certificate) "$@"; exit;;
    cleanup) "$@"; exit;;
esac

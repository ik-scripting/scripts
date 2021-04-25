#!/bin/bash -e
# https://linux.die.net/man/1/ssh-keygen
#
#   Copyright 2018 Ivan Katliarchuk
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# Usage
# curl -s "https://raw.githubusercontent.com/ik-scripting/scripts/master/ssh/create.ssh-key.sh" | bash -s arg1 arg2 arg3
# wget "https://raw.githubusercontent.com/ik-scripting/scripts/master/ssh/create.ssh-key.sh" && chmod +x create.ssh-key .sh && create.ssh-key.sh
#

KEY_SIZE=4096
KEY_TYPE="rsa"

SSH_KEYGEN=`which ssh-keygen`
CHMOD=`which chmod`

if [ -z "$SSH_KEYGEN" ];then
    echo Could not find the 'ssh-keygen' executable
    exit 1
fi

if [ -z "$CHMOD" ];then
    echo Could not find the 'chmod' executable
    exit 1
fi

function usage(){
  echo -e "usage: $0 [COMMENT] [PASSPHRASE] [KEYNAME]\n"
  echo -e 'COMMENT\t\t Provides a new comment.'
  echo -e 'PASSPHRASE\t Provides the new passphrase.'
  echo -e 'KEYNAME\t\t Specifies the filename of the key file.'
}

HELP=0

COMMENT=$1
PASSPHRASE=$2
KEYNAME=$3
KEY_PATH=~/.ssh/

function log_error() {
  echo -e "ERROR: $*\n"
  HELP=1
}

if [[ -z $COMMENT ]]; then
  log_error 'You must specify a comment.'
fi

if [[ -z $PASSPHRASE ]]; then
  log_error 'You must specify a passphrase.'
fi

if [[ -z $KEYNAME ]]; then
  log_error 'You must specify a keyname.'
fi

if [[ -z $KEY_PATH ]]; then
  log_error 'You must specify a directory folder.'
fi

if [[ $HELP = "1" ]]; then
  usage
  exit 1
fi

FILENAME="${KEY_PATH}${KEYNAME}"

echo "============================================"
echo "Generating public/private rsa key pair"
echo "Key Name to Create ${KEYNAME}"
echo "Desired Path ${KEY_PATH}"
echo "FIle Name ${FILENAME}"
echo "Comment ${COMMENT}"
echo "Passphrase ${PASSPHRASE}"
echo "============================================"
# -P instead of N for old keys
${SSH_KEYGEN} -t "${KEY_TYPE}" -b "${KEY_SIZE}" -C "${COMMENT}" -N "${PASSPHRASE}" -f "${FILENAME}"

echo "Adjust permissions of generated key-files locally."
${CHMOD} 0600 "${FILENAME}" "${FILENAME}.pub"
RET=$?
if [ $RET -ne 0 ];then
    echo chmod failed: $RET
    exit 1
fi

echo "Show all files in ${KEY_PATH} location"
ls -la "${KEY_PATH}"
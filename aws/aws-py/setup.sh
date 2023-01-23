#!/usr/bin/env bash

set -e

# load build variables
VIRTUAL_ENVIRONMENT="veenv"

ROOTDIR=`dirname $0`
REQUIREMENTS=py/requirements.txt
TEST_REQUIREMENTS=tests/requirements.txt

# create virtual environemnt
if [ "${CONFIG}" = "" ]
then
  if [ ! -d "${ROOTDIR}/${VIRTUAL_ENVIRONMENT}" ]; then
    virtualenv --python=/usr/bin/python2.7 ${ROOTDIR}/${VIRTUAL_ENVIRONMENT} --no-site-packages
    echo "Virtualenv ${VIRTUAL_ENVIRONMENT} created."
  fi
  source "$ROOTDIR/${VIRTUAL_ENVIRONMENT}/bin/activate"
  echo "virtualenv ${VIRTUAL_ENVIRONMENT} activated."
fi

pip install --upgrade pip

pip install -r $REQUIREMENTS -r $TEST_REQUIREMENTS
#cp $REQUIREMENTS $ROOTDIR/${VIRTUAL_ENVIRONMENT}/updated
echo "Requirements installed."

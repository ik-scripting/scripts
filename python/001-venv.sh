#!/usr/bin/env bash

set -e

# load build variables
source buildVars

ROOTDIR=`dirname $0`
REQUIREMENTS=`dirname $0`/requirements

ls -la $ROOTDIR

# create virtual environemnt
if [ ! -d "${ROOTDIR}/${VIRTUAL_ENVIRONMENT}" ]; then
    virtualenv -q ${ROOTDIR}/${VIRTUAL_ENVIRONMENT} --no-site-packages
    echo "Virtualenv ${VIRTUAL_ENVIRONMENT} created."
fi

if [ ! -f "$ROOTDIR/${VIRTUAL_ENVIRONMENT}/updated" -o $REQUIREMENTS -nt $ROOTDIR/${VIRTUAL_ENVIRONMENT}/updated ]; then
    source "$ROOTDIR/${VIRTUAL_ENVIRONMENT}/bin/activate"
    echo "virtualenv ve-boto3-cloudformation activated."

    pip install --upgrade pip

    pip install -r $REQUIREMENTS
    cp $REQUIREMENTS $ROOTDIR/${VIRTUAL_ENVIRONMENT}/updated
    echo "Requirements installed."
fi

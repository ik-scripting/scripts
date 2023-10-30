#! /bin/bash

# https://daveshepherd.uk/2018-04-privilege-escalation-in-vault
################################################################################
# Wraps the Vault CLI to escalate privileges for updating and deleting secrets #
# Add it to your path and then you can just call it as sudo-vault passing the  #
# Same parameters you would if you were using the Vault CLI directly.          #
################################################################################

VAULT=$(which vault)
[[ -z ${VAULT} ]] && echo 'ERROR: Vault command not found in the search path. exiting...' && exit 1

[[ -z ${APP_ROLE_NAME} ]] && APP_ROLE_NAME=power-user

echo -n "You are working with increased privileges - do you know what you're doing (y/n)? "
read answer
if echo "$answer" | grep -iq "^y"; then
    if ${VAULT} token lookup > /dev/null 2>&1 ; then

        VAULT_ROLE_ID=$(${VAULT} read -field=role_id auth/approle/role/${APP_ROLE_NAME}/role-id)
        VAULT_SECRET_ID=$(${VAULT} write -f -field=secret_id auth/approle/role/${APP_ROLE_NAME}/secret-id)
        VAULT_TOKEN=$(${VAULT} write -field=token auth/approle/login role_id=${VAULT_ROLE_ID} secret_id=${VAULT_SECRET_ID})

        VAULT_TOKEN=${VAULT_TOKEN} ${VAULT} $@
        exit $?
    else
        echo "Not logged in, log into Vault and try again"
        exit 1
    fi
else
    echo "Exiting..."
    exit 1
fi
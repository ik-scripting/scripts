#! /bin/bash

vault token create -policy=transit_admin
export APP_ORDER_TOKEN=$(vault token create -policy=transit_admin -format=json | jq -r '.auth | .client_token')
# not working
VAULT_TOKEN="$TEMP_TOKEN" vault write -format=json transit/encrypt/journey-personaldata plaintext=YXNkZndlYXR3ZXRldwo=
VAULT_TOKEN="$TEMP_TOKEN" vault policy list
vault token create -policy=transit_admin
vault policy list
vault write transit/key/test type=aes256-gcm96
vault write transit/encrypt/test plaintext=$(base64 <<< "my secret data")
vault policy list
export VAULT_TOKEN=$(vault token create -policy=super_admin -format=json | jq -r '.auth | .client_token')
curl -H "X-Vault-Token: $(vault print token)" -H "X-Vault-Request: true" $VAULT_ADDR/v1/transit/config/keys
curl -H "X-Vault-Token: $(vault print token)" -H "X-Vault-Request: true" $VAULT_ADDR/v1/transit-v2/config/keys

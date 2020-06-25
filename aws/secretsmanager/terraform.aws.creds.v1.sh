#!/bin/bash

set -euo pipefail

: $ENVIRONMENT

COMMAND=${1:-plan}
OPTS=
[ "$COMMAND" = plan ] || OPTS=-auto-approve

scripts/get_state.sh -e $ENVIRONMENT -f $ENVIRONMENT.json -f $ENVIRONMENT-rds.tfstate

log() {
	echo  -e "$1"
}

secretsmanager_get() {
	aws secretsmanager get-secret-value \
		--secret-id "$ENVIRONMENT/sqlserver/secret" \
		| jq -r '.SecretString' \
		| jq -r ".$1"
}

parameter_get() {
	aws ssm get-parameter --name "/$ENVIRONMENT/api/db_user" \
		--with-decryption | jq -r '.Parameter' | jq -r '.Value'
}

save_state() {
	log ""
  log "exiting ..."
}
trap save_state EXIT

DB_ROOT_USERNAME=$(secretsmanager_get root_user)
DB_ROOT_PASSWORD=$(secretsmanager_get root_password)
DB_PORT=$(secretsmanager_get db_port)
DB_HOST=$(secretsmanager_get db_host)

log "DB Host: $DB_HOST"
log "DB Root Password: $DB_ROOT_PASSWORD"
log "DB Root Username: $DB_ROOT_USERNAME"
log "DB Username: $(secretsmanager_get user)"
log "DB Password: $(secretsmanager_get password)"

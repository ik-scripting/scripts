#!/usr/bin/env bash

# bash and curl is required, so that health check works correctly

set -e

if [ ! -z "${APP_ENV_VALUES:-}" ]; then
  echo "APP_ENV_VALUES found"
  echo "${APP_ENV_VALUES}" > values.env
  unset APP_ENV_VALUES
  echo "sourced 'APP_ENV_VALUES' from 'values.env' file"

  while IFS= read -r line; do
    KEY="${line%%=*}"
    VALUE="${line##*=}"
    if [ !  -z "${KEY}" ];then
      echo "set: $KEY"
      export ${line}
    fi
  done < values.env
fi

exec "$@"
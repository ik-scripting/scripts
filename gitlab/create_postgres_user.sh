#!/usr/bin/env bash

# https://gitlab.com/gitlab-org/gitlab-foss/-/blob/master/scripts/create_postgres_user.sh

psql -h postgres -U postgres postgres <<EOF
CREATE USER gitlab;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gitlab;
EOF

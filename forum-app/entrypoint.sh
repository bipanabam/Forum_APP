#!/bin/bash

set -e

# set the postgres database host, port, user and password according to the environment
# and pass them as arguments to the odoo process if not present in the config file
: ${HOST:=${DB_HOST:='db'}}
: ${PORT:=${DB_PORT:=5432}}
: ${USER:=${DB_USER:='user'}}
: ${PASSWORD:=${DB_PASSWORD:='password'}}

DB_ARGS=()
function check_config() {
    param="$1"
    value="$2"
    DB_ARGS+=("--${param}")
    DB_ARGS+=("${value}")
}
check_config "db_host" "$HOST"
check_config "db_port" "$PORT"
check_config "db_user" "$USER"
check_config "db_password" "$PASSWORD"

case "$1" in
    flask)
        wait-for-psql.py ${DB_ARGS[@]} --timeout=60
        exec python app.py
        ;;
    *)
        exec "$@"
esac

exit 1
#!/usr/bin/env bash

set -e
set -u
set -o pipefail

show_help() {
cat << EOF
Usage: $(basename "$0") <options>
    -h, --help       Display help
    -v, --verbose    Display verbose output
    -n, --namespace  The namespace Keycloak runs in (default: dev)
    -a, --action     The action to perform (import|export)
    -d, --dir        The json file to import from or export to (default: impex)
EOF
}

main() {
    local verbose=
    local action=
    local namespace=dev
    local dir=impex

    while :; do
        case "${1:-}" in
            -h|--help)
                show_help
                exit
                ;;
            -v|--verbose)
                verbose=true
                ;;
            -a|--action)
                case "${2:-}" in
                    import|export)
                        action="$2"
                        shift
                        ;;
                    *)
                        echo "ERROR: '-a|--action' does not match (import|export)." >&2
                        show_help
                        exit 1
                        ;;
                esac
                ;;
            -n|--namespace)
                if [ -n "${2:-}" ]; then
                    namespace="$2"
                    shift
                else
                    echo "ERROR: '-n|--namespace' cannot be empty." >&2
                    show_help
                    exit 1
                fi
                ;;
            -d|--dir)
                if [ -n "${2:-}" ]; then
                    dir="$2"
                    shift
                else
                    echo "ERROR: '-d|--dir' cannot be empty." >&2
                    show_help
                    exit 1
                fi
                ;;
            *)
                break
                ;;
        esac

        shift
    done

    if [[ -z "$action" ]]; then
        echo "ERROR: '-a|--action' is required." >&2
        show_help
        exit 1
    fi

    [[ -n "$verbose" ]] && set -x

    impex "$namespace" "$action" "$dir"
}

impex() {
    local namespace="$1"
    local action="$2"
    local dir="$3"

    local server_dir
    server_dir="/opt/jboss/$(basename "$dir")"

    local log_file
    log_file="/opt/jboss/$action.log"

    # shellcheck disable=SC2064
    trap "cleanup '$namespace' '$server_dir' '$log_file'" EXIT

    if [[ "$action" == 'import' ]]; then
        echo "Copying '$dir' to Keycloak container..."
        kubectl cp --namespace "$namespace" "$dir" "keycloak-0:$server_dir"
    fi

    local cmd
    cmd=$(create_impex_cmd "$namespace" "$action" "$dir" "$server_dir")

    kubectl exec --namespace "$namespace" keycloak-0 -- sh -c "$cmd"

    echo "Copying '$action.log' from container..."
    kubectl cp --namespace "$namespace" "keycloak-0:$log_file" .

    if [[ "$action" == 'export' ]]; then
        echo "Copying '$dir' from Keycloak container..."
        kubectl cp --namespace "$namespace" "keycloak-0:$server_dir" "$dir"
    fi
}

create_impex_cmd() {
    local namespace="$1"
    local action="$2"
    local dir="$3"
    local server_dir="$4"

    cat << EOF
# Start up non-HA Keycloak for impex only using different ports
echo "Starting up Keycloak $action instance..."

# JAVA_OPTS configures the heap. If we reuse this here we get an additional container
# with the same amount of heap. The pod would get OOMKilled.
unset JAVA_OPTS

/opt/jboss/keycloak/bin/standalone.sh \
    -Dkeycloak.migration.action="$action" \
    -Dkeycloak.migration.dir="$server_dir" \
    -Dkeycloak.migration.strategy=OVERWRITE_EXISTING \
    -Dkeycloak.migration.usersExportStrategy=SAME_FILE \
    -Djboss.http.port=8888 \
    -Djboss.https.port=9999 \
    -Djboss.management.http.port=7777 > "$action.log" &

pid="\$!"

echo "Waiting for Keycloak $action instance to start up..."
until grep 'Deployed "keycloak-server.war"' "$action.log" ; do
    printf '.'
    sleep 1
done

echo '✓'

echo "Shutting down Keycloak $action instance..."
kill "\$pid"
EOF
}

cleanup() {
    local namespace="$1"
    local server_dir="$2"
    local log_file="$3"

    echo 'Performing clean-up...'
    kubectl exec --namespace "$namespace" keycloak-0 -- rm -rf "$server_dir" "$log_file"

    echo 'Done.'
}

main "$@"

#!/usr/bin/env bats

set -o pipefail
load helper

INGRESS_ROUTES_MIN=2

# The client function
DETIK_CLIENT_NAME="kubectl"
# If you want to work in a specific namespace.
# If not set, queries will be run in the default namespace.
DETIK_CLIENT_NAMESPACE="apps"

setup() {
	echo "Test 'Treafik' ingress in 'apps' namespace"
}

@test "should not have Traefik deployed in 'apps' namespace" {
	run verify "there are 0 pods named 'traefik-external'"
	[ "$status" -eq 0 ]
}

@test "should have traefik IngressRoutes in 'apps' namespace" {
	actual=`kubectl get IngressRoutes -n ${DETIK_CLIENT_NAMESPACE} | wc -l | xargs`
	min_value_met $INGRESS_ROUTES_MIN $actual
}

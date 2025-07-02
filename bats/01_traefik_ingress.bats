#!/usr/bin/env bats

set -o pipefail
load helper

TRAEFIK_PODS_EXPECTED=2

# The client function
DETIK_CLIENT_NAME="kubectl"
# If you want to work in a specific namespace.
# If not set, queries will be run in the default namespace.
DETIK_CLIENT_NAMESPACE="ingress"

setup() {
  echo "Test 'Treafik' in 'ingress' namespace"
}

@test "should have Traefik deployed" {
  # TODO: parametrize in the future
	run verify "there are $TRAEFIK_PODS_EXPECTED pods named 'traefik-external'"
	[ "$status" -eq 0 ]

  run verify "there are $TRAEFIK_PODS_EXPECTED pods named 'traefik-internal'"
	[ "$status" -eq 0 ]
  assert_line "Found $TRAEFIK_PODS_EXPECTED pods named traefik-internal (as expected)."

  run verify "there are 8 services named 'traefik'"
	[ "$status" -eq 0 ]
  assert_line "Found 8 services named traefik (as expected)."
  debug "Command output is: $output"
}

@test "should verify Traefik properties (with retries)" {
  try "at most 5 times every 5s to get pods named 'traefik' and verify that 'status' is 'RUNNING'"
}

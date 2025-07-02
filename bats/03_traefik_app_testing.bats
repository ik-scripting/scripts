#!/usr/bin/env bats

set -o pipefail
load helper

API_HOST=https://paas-1072-internal-eks.eu-west-1.sandbox.hbi.systems

# The client function
DETIK_CLIENT_NAME="kubectl"
# If you want to work in a specific namespace.
# If not set, queries will be run in the default namespace.
DETIK_CLIENT_NAMESPACE="apps"

setup() {
	echo "Test apps."
}

api_call() {
	run curl -i $API_HOST/foo/bar
	[ "$status" -eq 0 ]
	assert_output --partial 'HTTP/2 200'
	assert_output --partial '/:path1/:path2 - Hello to foo/bar'
}

@test "should API be accesible" {
	# TODO: its a temporary app, deploy similar app to all three environment
	run curl -i $API_HOST/foo/bar
	[ "$status" -eq 0 ]
	assert_output --partial 'HTTP/2 200'
	assert_output --partial '/:path1/:path2 - Hello to foo/bar'
}

@test "should API be accesible. Multiple calls" {
	for i in {1..5}; do
		api_call
	done
}

@test "verify a real deployment" {
	skip
	# TODO; deploy real app
}

@test "verify an s3 static deployment" {
	skip
	# TODO; deploy real app with s3 static
}

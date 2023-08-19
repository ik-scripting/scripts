#!/usr/bin/env bash

start_json="{\"script\": \"$0\"}"
echo "$start_json"
runner_script_trap() {
	exit_code=$?
	out_json="{\"command_exit_code\": $exit_code, \"script\": \"$0\"}"

	echo ""
	echo "$out_json"
	exit 0
}

trap runner_script_trap EXIT
if set -o | grep pipefail > /dev/null; then set -o pipefail; fi; set -o errexit

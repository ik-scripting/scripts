#!/usr/bin/env bash

load '../bin/support/load' # this is required by bats-assert!
load '../bin/assert/load'
load '../bin/detik/lib/utils'
load '../bin/detik/lib/detik'

# shellcheck disable=SC2154
assert_success() {
  if [[ "$status" != 0 ]]; then
    echo "expected: 0"
    echo "actual: $status"
    echo "output: $output"
    return 1
  fi
}

assert_failure() {
  if [[ "$status" == 0 ]]; then
    echo "expected: non-zero exit code"
    echo "actual: $status"
    echo "output: $output"
    return 1
  fi
}

assert_equal() {
  if [[ "$1" != "$2" ]]; then
    echo "expected: ${1}"
    echo "actual: ${2}"
    return 1
  fi
}

assert_not_equal() {
  if [[ "${1}" == "${2}" ]]; then
    echo "unexpected: ${1}"
    echo "actual: ${2}"
    return 1
  fi
}

assert_match() {
  if [[ ! "$2" =~ ${1} ]]; then
    echo "expected: $1"
    echo "actual: $2"
    return 1
  fi
}

assert_not_match() {
  if [[ "$2" =~ ${1} ]]; then
    echo "expected: $1"
    echo "actual: $2"
    return 1
  fi
}

# values_equal takes 2 values, both must be non-null and equal
values_equal() {
  if [[ "X$1" != "X" ]] || [[ "X$2" != "X" ]] && [[ $1 == "${2}" ]]; then
    return 0
  else
    return 1
  fi
}
wait-for-code() {
  count=0
  while [ "${count}" -le 24 ]; do
    "${1}"
    if [ "${status}" -eq "${2}" ]; then
      break
    else
      count=$((count + 1))
      sleep 5
    fi
  done
}

# min_value_met takes 2 values, both must be non-null and 2 must be equal or greater than 1
min_value_met() {
  if [[ "X${1}" != "X" ]] || [[ "X${2}" != "X" ]] && [[ "${2}" -ge "${1}" ]]; then
    return 0
  else
    echo "ERROR::min_value_not_met() expected:$1 actual:$2" >&3
    return 1
  fi
}

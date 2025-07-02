#!/usr/bin/env bats

@test "should have bats installed" {
  result="$(echo 2+2 | bc)"
  [ "$result" -eq 4 ]
}

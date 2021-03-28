#!/usr/bin/env bats

@test "Team namespaces can scale deployments within their own namespace" {
    run kubectl auth can-i update deployments.apps --subresource="scale" --as-group="$group" --as="$user" -n $ns
    [ "$status" -eq 0 ]
    [ "$output" == "yes" ]
  done
}

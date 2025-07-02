# -*- coding: utf-8 -*-

# Documentation
# https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/
# https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/#take-snapshots

# How to run python
# scripts/snapshot-backup.py --env $CLI_ENV --domain $CLI_DOMAIN

from utils import read_json_file, request, arguments
from datetime import datetime

def only_oldest_snapshots(input, num_snapshots=3):
    """
    Keeps only the specified number of older snapshots in the JSON data.

    Args:
        input: The JSON data as a Python dictionary.
        num_snapshots: The number of older snapshots to keep.

    Returns:
        The modified JSON data with only the older snapshots.
    """

    snapshots = input
    snapshots.sort(key=lambda x: x['start_time_in_millis'], reverse=True)
    return snapshots[num_snapshots:]

def snapshot_list(endpoint):
    # Retrieving existing snapshots
    # https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/#restore-snapshots
    url = f"{endpoint}/_snapshot/default/_all"
    return request(url, "GET")

def snapshot_cleanup(endpoint, snapshots):
    # Deletes a snapshot from a repository.
    # https://opensearch.org/docs/latest/api-reference/snapshots/delete-snapshot/
    # TODO: implement cleanup
    pass

def snapshot_create(endpoint, wait):
    # https://opensearch.org/docs/latest/api-reference/snapshots/create-snapshot/
    time = datetime.now().strftime("%Y-%m-%d-%H-%M")
    name=f"snap-{time}"
    url = f"{endpoint}/_snapshot/default/{name}?wait_for_completion={wait.lower()}"
    print(f"take incremental snapshot '{name}'.")
    payload={
        "indices": "-.kibana*,-.opendistro*,-.plugins*",
        "ignore_unavailable": "true",
        "include_global_state": "false"
    }
    return request(url, "PUT", payload=payload)

if __name__ == "__main__":
    args = arguments()
    data = read_json_file(args.config)

    domain_endpoint = data[args.env][args.domain]

    print("****************************")
    print(f"env '{args.env}'")
    print(f"domain '{args.domain}'")
    print(f"endpoint '{domain_endpoint}'")
    print("****************************")

    snapshots = snapshot_list(domain_endpoint)
    # can only take & cleanup snapshots for clusters without prefix -dr
    if "-dr" not in domain_endpoint:
        snapshot_cleanup(domain_endpoint, only_oldest_snapshots(snapshots['snapshots']))
        snapshot_create(domain_endpoint, args.wait)

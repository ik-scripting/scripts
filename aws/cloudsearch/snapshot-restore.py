# -*- coding: utf-8 -*-

# Documentation
# https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/#restore-snapshots
# https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/#conflicts-and-compatibility

from utils import read_json_file, request, arguments
from datetime import datetime

path = "_snapshot/default"

def latest_snapshots(input, num_snapshots=1):
    """
    Keeps only the specified number of latest snapshots in the JSON data.

    Args:
        input: The JSON data as a Python dictionary.
        num_snapshots: The number of snapshots to keep.

    Returns:
        JSON data with only the latest snapshots.
    """
    snapshots = input['snapshots']
    snapshots.sort(key=lambda x: x['start_time_in_millis'], reverse=True)
    return snapshots[:num_snapshots]

def snapshot_list(endpoint):
    # Retrieving existing snapshots
    # https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/#restore-snapshots
    url = f"{endpoint}/{path}/_all"
    return request(url, "GET")

def snapshot_get(endpoint, snapshot_id):
    # Retrieving existing snapshots
    # https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/#restore-snapshots
    url = f"{endpoint}/{path}/{snapshot_id}"
    return request(url, "GET")

def snapshot_restore(endpoint, snapshots):
    # Restore existing snapshot
    # https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/#restore-snapshots
    # https://opensearch.org/docs/latest/api-reference/snapshots/restore-snapshot/
    if len(snapshots) > 1:
        raise Exception("Should only have single snapshot.")
    snapshot=snapshots[0]
    snapshot_id=snapshot['snapshot']
    snapshot_get(endpoint, snapshot_id)
    url = f"{endpoint}/{path}/{snapshot_id}/_restore?wait_for_completion=true"
    time = datetime.now().strftime("%Y.%m.%d.%H.%M")
    payload={
        "indices": "-.kibana*,-.opendistro*,-.plugins*",
        "ignore_unavailable": "true",
        "include_aliases": "false",
        "rename_pattern": "(.+)",
        "rename_replacement": f"$1_restored_{time}",
        "include_global_state": "false"
    }
    print("payload", payload)
    # TODO: uncomment in follow up pull request
    # return request(url, method="POST", payload=payload)

if __name__ == "__main__":
    args = arguments()
    data = read_json_file(args.config)

    domain_endpoint = data[args.env][args.domain]

    print("****************************")
    print(f"snapshot restore 4")
    print(f"env '{args.env}'")
    print(f"domain '{args.domain}'")
    print(f"endpoint '{domain_endpoint}'")
    print("****************************")

    snapshots = snapshot_list(domain_endpoint)
    latest = latest_snapshots(snapshots)
    # only restore snapshot with domains that contain suffix -dr
    # this is a temporary solution, but we should not allow snapshot restore to live domains
    if "-dr" in args.domain:
        snapshot_restore(domain_endpoint, latest)
    else:
        print("skip snapshot restore. data restore for live domains not supported")


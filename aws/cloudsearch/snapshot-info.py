# -*- coding: utf-8 -*-

# How to run python scripts/snapshot-info.py --env $CLI_ENV --domain $CLI_DOMAIN

# https://opensearch.org/docs/latest/api-reference/remote-info/
from utils import read_json_file, request, arguments

def get_os_health(domain_endpoint):
    # The health check endpoint
    # https://opensearch.org/docs/2.14/api-reference/cluster-api/cluster-health/
    url = f"{domain_endpoint}/_cluster/health?wait_for_status=green&timeout=50s"
    print("request cluster health check")
    return request(url, "GET")

def get_os_snapshot_verify(domain_endpoint):
    # The health check endpoint
    # https://opensearch.org/docs/latest/api-reference/snapshots/verify-snapshot-repository/#path-parameters
    print("verifies that a snapshot repository is functional.")
    url = f"{domain_endpoint}/_snapshot/default"
    return request(url, "GET")

def get_os_indices(domain_endpoint):
    # The health check endpoint
    # https://docs.aws.amazon.com/opensearch-service/latest/developerguide/handling-errors.html
    print("If cluster health is green, check that all expected indexes are present using the following request.")
    url = f"{domain_endpoint}/_cat/indices"
    return request(url, "GET", "text")

def get_os_list_snapshots(domain_endpoint):
    # Retrieving existing snapshots
    # https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/#restore-snapshots
    url = f"{domain_endpoint}/_snapshot/default/_all"
    return request(url, "GET")

if __name__ == "__main__":
    args = arguments()
    data = read_json_file(args.config)

    domain_endpoint = data[args.env][args.domain]

    print("****************************")
    print(f"env '{args.env}'")
    print(f"domain '{args.domain}'")
    print(f"endpoint '{domain_endpoint}'")
    print("****************************")

    get_os_health(domain_endpoint)
    get_os_indices(domain_endpoint)
    get_os_snapshot_verify(domain_endpoint)
    get_os_list_snapshots(domain_endpoint)

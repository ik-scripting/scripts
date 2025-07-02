# -*- coding: utf-8 -*-

# Documentation
# https://opensearch.org/docs/latest/api-reference/snapshots/restore-snapshot/
# https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/#restore-snapshots
# https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/#conflicts-and-compatibility

# WARNING. This DSL is required only in cases when index exist, but is not configured correctly or there is missing data and we planning to restore it
# How to run
# 1. Prepare environment
# 1.1 pipenv shell
# 1.1 pip install boto3; pip install requests; pip install requests_aws4auth
# 2. Run DSL
# 2. CLI_INDEX_ID=abrakadabra
# 2.1 python scripts/index-restore.py --env $CLI_ENV --config config.json --domain $CLI_DOMAIN --repository-name you-repo-name --index-id $CLI_INDEX_ID

from utils import read_json_file, request, arguments, json_prettify

def index_restore(endpoint, repository, index):
    path = f"_snapshot/{repository}"
    url = f"{endpoint}/{path}/{index}/_restore?wait_for_completion=true"
    payload={
        "indices": "orders-v1-data-2021",
        "ignore_unavailable": "true",
        "include_aliases": "false",
        "include_global_state": "false"
    }
    print(f"POST for '{url}' with 'index:{index}' and paylod '{json_prettify(payload)}'")
    return request(url, method="POST", payload=payload)

if __name__ == "__main__":
    args = arguments()
    data = read_json_file(args.config)

    domain_endpoint = data[args.env][args.domain]

    print("************ index restore ****************")
    print(f"env '{args.env}'")
    print(f"domain '{args.domain}'")
    print(f"endpoint '{domain_endpoint}'")
    print(f"index to restore '{args.index_id}'")
    print("****************************")

    if args.index_id and args.repository_name:
        index_restore(domain_endpoint, args.repository_name, args.index_id)

# -*- coding: utf-8 -*-

# Documentation
# https://opensearch.org/docs/latest/api-reference/index-apis/delete-index/
# https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/#take-snapshots

# How to run
# 1. Prepare environment
# 1.1 pipenv shell
# 1.1 pip install boto3; pip install requests; pip install requests_aws4auth
# 2. Run DSL
# 2. CLI_INDEX_ID=abrakadabra
# 2.1 python scripts/index-delete.py --env $CLI_ENV --config config.json --domain $CLI_DOMAIN --repository-name default --index-id $CLI_INDEX_ID

from utils import read_json_file, request, arguments

def index_cleanup(endpoint, index):
    # Deletes a snapshot from a repository.
    # https://opensearch.org/docs/latest/api-reference/index-apis/delete-index/
    url = f"{endpoint}/{index}"
    print(f"DELETE for '{url}' with 'index:{index}'")
    request(url, "DELETE")

if __name__ == "__main__":
    args = arguments()
    data = read_json_file(args.config)

    domain_endpoint = data[args.env][args.domain]

    print("************ index cleanup ****************")
    print(f"env '{args.env}'")
    print(f"domain '{args.domain}'")
    print(f"endpoint '{domain_endpoint}'")
    print(f"index to cleanup '{args.index_id}'")
    print("****************************")

    if args.index_id:
        index_cleanup(domain_endpoint, args.index_id)

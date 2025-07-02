# -*- coding: utf-8 -*-

# Requred in cases when backup is not longer required
# ref: https://opensearch.org/docs/latest/api-reference/snapshots/delete-snapshot/
# ref: https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/

# How to run
# 1. Prepare environment
# 1.1 pipenv shell
# 1.1 pip install boto3; pip install requests; pip install requests_aws4auth
# 2. Run DSL
# 2.1 python scripts/backup-delete.py --env $CLI_ENV --config config.json --domain $CLI_DOMAIN --repository-name default --snapshot-id $CLI_BACKUP_ID

from utils import read_json_file, request, arguments


def snapshot_cleanup(endpoint, repository, snapshot):
    url = f"{endpoint}/_snapshot/{repository}/{snapshot}"
    print(f"deleting backup '{url}' with snapshot id '{snapshot}'")
    request(url, "DELETE")

if __name__ == "__main__":
    args = arguments()
    data = read_json_file(args.config)

    domain_endpoint = data[args.env][args.domain]

    print("****************************")
    print(f"env '{args.env}'")
    print(f"domain '{args.domain}'")
    print(f"endpoint '{domain_endpoint}'")
    print("****************************")

    if args.snapshot_id:
        snapshot_cleanup(domain_endpoint, args.repository_name, args.snapshot_id)

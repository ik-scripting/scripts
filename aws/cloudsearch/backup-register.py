# -*- coding: utf-8 -*-

# Requred in cases when backup restore required from OS1 to OS2
# ref: https://opensearch.org/docs/latest/api-reference/snapshots/create-repository/

# How to run
# 1. Prepare environment
# 1.1 pipenv shell
# 1.1 pip install boto3; pip install requests; pip install requests_aws4auth
# 2. Run DSL
# 2.1 python scripts/backup-register.py --env $CLI_ENV --config config.json --domain $CLI_DOMAIN --repository-name shared-restore

from utils import read_json_file, arguments, json_prettify
from requests_aws4auth import AWS4Auth
import boto3
import requests

bucket="hbi-paas-es-manual-snapshots-prod"
base_path="sc-oms/shared-restore"
path = f'_snapshot/shared-restore'
headers = {"Content-Type": "application/json"}
region = 'eu-west-1'
service = 'es'

def register(host, repository):
    payload = {
        "type": "s3",
        "settings": {
            "bucket": "hbi-paas-es-manual-snapshots-prod",
            "region": region,
            "base_path": f'sc-oms/{repository}',
            # hardcoded IAM role. Required to be same across all OS clusters if restoring cross-snapshot backups
            "role_arn": "arn:aws:iam::00000000:role/es-snapshots-oms-search-aws-restored"
        }
    }
    url = f'{host}/{path}'
    print(f"registration url '{url}' with payload '{json_prettify(payload)}'")
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    r = requests.put(url, auth=awsauth, json=payload, headers=headers)
    print(r.status_code)
    print(r.text)


if __name__ == "__main__":
    args = arguments()
    data = read_json_file(args.config)

    domain_endpoint = data[args.env][args.domain]

    print("****************************")
    print(f"env '{args.env}'")
    print(f"domain '{args.domain}'")
    print(f"endpoint '{domain_endpoint}'")
    print("****************************")

    print(args)

    register(domain_endpoint, args.repository_name)

# -*- coding: utf-8 -*-

import json, argparse, os, uuid
import requests, boto3

def read_json_file(file):
    with open(file) as f:
        d = json.load(f)
    return d

def json_prettify(data):
    return json.dumps(data, indent=4, default=str)

def request(endpoint_url, method="GET", content="json", payload=None):
    """
    Makes a request to the specified OpenSearch endpoint URL and returns JSON response data.

    Args:
        endpoint_url (str): Full URL for the OpenSearch endpoint.
        description (str): Description of the request's purpose (for logging).
        method (str): HTTP method for the request (e.g., "GET", "PUT").
        payload (dict, optional): JSON payload for PUT requests.

    Returns:
        dict: JSON data returned from the request.
    """
    print(f"Request method: '{method}',  URL: '{endpoint_url}' and payload: '{payload}'")
    try:
        if method.upper() == "GET":
            response = requests.get(endpoint_url)
        elif method.upper() == "PUT":
            response = requests.put(endpoint_url, json=payload)
        elif method.upper() == "POST":
            response = requests.post(endpoint_url, json=payload)
        elif method.upper() == "DELETE":
            response = requests.delete(endpoint_url)
        else:
            raise ValueError("Unsupported HTTP method: Only 'GET' and 'PUT' are supported.")

        response.raise_for_status()
        if content == 'json':
            data = response.json()
            print("Response Data:", json.dumps(data, indent=2))
        else:
            data = response.text
            print("Response Data:", data)
        return data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the request: {e}")
        if response is not None:
            print(response.text)
        raise

def aws4auth():
    session = boto3.Session()
    sts_client = boto3.client('sts')
    account_id = sts_client.get_caller_identity().get('Account')
    role_arn=f"arn:aws:iam::{account_id}:role/gitlab-ci-paas-es-restore-backup"
    session_name=f"es-create-backup-{str(uuid.uuid4())}"

    try:
            response = sts_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=session_name,
            )
            creds = response["Credentials"]
            print(f"Assumed role '{role_arn}' and session '{session_name}'.")
    except Exception as e:
        print(f"couldn't assume role {role_arn}. here's why: {e}")
        raise

    return AWS4Auth(
        creds["AccessKeyId"],
        creds["SecretAccessKey"],
        session.region_name,
        'es',
        session_token=creds["SessionToken"]
    )

def arguments():
    parser = argparse.ArgumentParser(description="ES and OS snapshot repository config.")
    parser.add_argument("--config", type=str, default="config.json", help="Config file location.")
    parser.add_argument("--env", type=str, help="Environment to run against.")
    parser.add_argument("--domain", type=str, help="Domain name.")
    parser.add_argument("--repository-name", type=str, default="default", help="Repository name. Required for shared restores.")
    parser.add_argument("--snapshot-id", type=str, help="Snapshot ID.")
    parser.add_argument("--index-id", type=str, help="Index ID.")
    parser.add_argument('--wait', type=str, default="true", help="Whether to wait for action to complete before continuing.")

    parser.parse_args()
    args = parser.parse_args()

    print("arguments:", args)

    if "help" in args:
        parser.print_help()
        os.exit(0)

    return args

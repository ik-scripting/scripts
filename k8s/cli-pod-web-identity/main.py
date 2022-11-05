#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Usage
# ./main.py --create
# ./main.py --create --template iam --namespace crossplane-system --svc "provider-aws-*"
# ./main.py --delete

# Create IAM role with Web Identity Federation
#
import os, logging, json
from datetime import datetime
import platform
import argparse
import boto3
import utils

default_log_args = {
    "level": logging.INFO,
    "format": "%(asctime)s [%(levelname)s] - %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}

logging.basicConfig(**default_log_args)
log = logging.getLogger("pod-web-identity")

sts_client = boto3.client('sts')
eks_client = boto3.client('eks')
iam_client = boto3.client('iam')
identity = sts_client.get_caller_identity()

NAME = "pod-web-identity"
CURRENT_DATE_TIME = datetime.now()
USER_ID= user_id=identity['UserId'].split(":")[1].lower()
ROLE_NAME = "eks-svc-pod-web-identity-test"
POLICY_NAME = f"{ROLE_NAME}-policy"
NAMESPACE = "default"
SERVICE_ACCOUNT = "pod-web-identity-test"

TAGS = [
    {
        'Key': 'created_by',
        'Value': USER_ID
    },
    {
        'Key': 'created_with',
        'Value': f"python3 {platform.python_version()}"
    },
    {
        'Key': 'created_at',
        'Value': CURRENT_DATE_TIME.strftime("%d/%m/%Y %H:%M")
    },
]

log.info(f'region: {sts_client.meta.region_name}')

def delete_role(id: str) -> None:
    policy_arn = f'arn:aws:iam::{id}:policy/{POLICY_NAME}'

    try:
        response = iam_client.get_role(
            RoleName= ROLE_NAME
        )
        response = iam_client.list_attached_role_policies(
            RoleName=ROLE_NAME
        )
        for el in response['AttachedPolicies']:
            iam_client.detach_role_policy(
                RoleName=ROLE_NAME,
                PolicyArn=el['PolicyArn']
            )
            iam_client.delete_policy(
                PolicyArn=policy_arn
            )
            log.info(f'policy "{POLICY_NAME}" detached and deleted')
        log.warning(f'role "{ROLE_NAME}" found and policies detached')
        iam_client.delete_role(
            RoleName=ROLE_NAME
        )
        log.info(f'role "{ROLE_NAME}" deleted')
    except iam_client.exceptions.NoSuchEntityException as e:
        log.warning(f'role "{ROLE_NAME}" not found, skipping...')
        return
    except Exception as e:
        log.warning(f'error when deleting role {ROLE_NAME}...')
        raise ValueError(e)


def create_role(
    id: str,
    cluster_name: str,
    namespace: str,
    service_account: str,
    role_template: str
    ) -> None:
    """
    Create IAM role

    :param id: account id
    :param region: aws region
    :type id: str
    :type region: str
    :returns: None
    :raises Exception if a role not found
    """
    policy_file_location = f"./policies/{role_template}.json"
    response = eks_client.describe_cluster(
        name=cluster_name
    )
    oidc_issuer =response["cluster"]["identity"]["oidc"]["issuer"].replace("https://", "")
    log.info(f'issuer: {oidc_issuer}')
    role = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Federated": f"arn:aws:iam::{account_id}:oidc-provider/{oidc_issuer}"
                },
                "Action": "sts:AssumeRoleWithWebIdentity",
                "Condition": {
                    "ForAnyValue:StringLike": {
                        f"{oidc_issuer}:sub": f"system:serviceaccount:{namespace}:{service_account}"
                    }
                }
            }
        ]
    }
    log.debug(role)
    try:
        response = iam_client.get_role(
            RoleName= ROLE_NAME
        )
        log.info(f'role found \"{response["Role"]["Arn"]}\"')
    except iam_client.exceptions.NoSuchEntityException as e:
        log.warning(f'role "{ROLE_NAME}" not found, creating ...')
        # function on its own
        role = iam_client.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(role),
            Description=f'role created with "{NAME}"',
            Tags=TAGS
        )
        log.info(f'role created "\{response["Role"]["Arn"]}\"')
    except Exception as e:
        raise ValueError(e)

    policy_arn = f'arn:aws:iam::{id}:policy/{POLICY_NAME}'
    try:
        policy = iam_client.get_policy(
            PolicyArn= policy_arn
        )
        log.debug(f'policy "{POLICY_NAME}" found')
        response = iam_client.create_policy_version(
            PolicyArn= policy_arn,
            PolicyDocument= utils.read_file(policy_file_location),
            SetAsDefault= True
        )
        # only 5 versions are allowed to have
        versions = iam_client.list_policy_versions(
            PolicyArn=policy_arn
        )
        for el in versions['Versions']:
            if el['IsDefaultVersion']:
                pass
            else:
                version = el['VersionId']
                iam_client.delete_policy_version(
                    PolicyArn=policy_arn,
                    VersionId=version
                )
                log.debug(f'policy "{policy_arn}" version "{version}" deleted ...')
        log.info(f'policy "{policy_arn}" updated...')
    except iam_client.exceptions.NoSuchEntityException as e:
        log.warning(f'policy "{POLICY_NAME}" not found, creating...')
        response = iam_client.create_policy(
            PolicyName=POLICY_NAME,
            PolicyDocument=utils.read_file(policy_file_location),
            Description=f'policy created with "{NAME}"',
            Tags=TAGS
        )
        log.info(f'policy "{POLICY_NAME}" created...')
        # raise NotImplementedError(f'role "{role_name}" no found')
    except Exception as e:
        raise ValueError(e)

    log.info(f'attaching policy "{POLICY_NAME}" to a role "{ROLE_NAME}" ...')
    iam_client.attach_role_policy(
        RoleName=ROLE_NAME,
        PolicyArn=policy_arn
    )
    log.info('attached')

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog=NAME,
        description="CLI to manage EKS web identity IAM role with policy'")

    parser.add_argument('--create', action='store_true', help="Create role with web identity and policy attached")
    parser.add_argument('--delete', action='store_true', help="Delete role with web identity")
    parser.add_argument('--cluster-name', default='eks-cluster-sandbox', type=str, help="Cluster to which the role should be attached")
    parser.add_argument('--namespace', default=NAMESPACE, type=str, help="namespace where create a trust.")
    parser.add_argument('--svc', default=SERVICE_ACCOUNT, type=str, help="service account for which create a role.")
    parser.add_argument('--template', default="s3-list", type=str, help="iam policy template.", choices=['iam', 's3-list'])

    args = parser.parse_args()
    account_id = identity['Account']

    if args.create:
        create_role(id=account_id, cluster_name = args.cluster_name,
                    namespace=args.namespace, service_account=args.svc, role_template=args.template)
    elif args.delete:
        delete_role(id=account_id)


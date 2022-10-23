#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Usage
# ./main.py --create
# ./main.py --delete

# Create IAM role with Web Identity Federation
#
import os, logging, json
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

def create_role(id: str, role_name: str,
                cluster_name: str, region: str,
                namespace: str, service_account: str) -> None:
    """

    Create IAM role

    :param id: account id
    :param region: aws region
    :type id: str
    :type region: str
    :returns: None
    :raises Exception if a role not found
    """
    response = eks_client.describe_cluster(
        name=cluster_name
    )
    oidc_issuer =response["cluster"]["identity"]["oidc"]["issuer"].replace("https://", "")
    # TODO: validate that contain region
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
    trust_relationship_policy_document = json.dumps(role)
    try:
        response = iam_client.get_role(
            RoleName= role_name
        )
        log.debug(f'role "{role_name}" found')
    except iam_client.exceptions.NoSuchEntityException as e:
        log.warning(f'role "{role_name}" no found')
        raise NotImplementedError(f'role "{role_name}" no found')
    except Exception as e:
        log.error(f'something failed')
        raise ValueError(e)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='pod-web-identity',
        description="CLI to manage EKS web identity IAM role with policy'")

    parser.add_argument('--create', action='store_true', help="Create role with web identity")
    parser.add_argument('--delete', action='store_true', help="Delete role with web identity")
    parser.add_argument('--cluster-name', default='eks-cluster-sandbox', type=str, help="Cluster to which the role should be attached")
    role_name = "eks-serviceaccount-pod-web-identity-test"
    namespace = "default"
    service_account = "pod-web-identity-test"

    args = parser.parse_args()

    identity = sts_client.get_caller_identity()

    account_id = identity['Account']

    if args.create:
        create_role(id=account_id, role_name=role_name,
                    region=sts_client.meta.region_name,
                    cluster_name = args.cluster_name,
                    namespace=namespace, service_account=service_account)
    elif args.delete:
        pass


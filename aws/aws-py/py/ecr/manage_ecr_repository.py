#!/usr/bin/env python
"""
 Add your own statements below to a policy document that allows others to access designated repository.
 Create/Update/Apply a repository policy to controll access permissions.
"""
import argparse
import json
import re

from context import create_context
from domain import Policy, Statement, Action

ACCOUNT_NUMBER_PATTERN = ".*?iam::(\d{12}):root"


def __attach_policy(client, account_id, repository_name, template_json):
    # set repository policy
    policytext = json.dumps(template_json, default=read_nested(), indent=4, sort_keys=False)
    print policytext
    try:
        client.set_repository_policy(
            registryId=account_id,
            repositoryName=repository_name,
            policyText=policytext,
            force=False
        )
    except Exception as e:
        raise EnvironmentError("Failed set policy {}".format(e.message))


def __enrich_template(template_json, sid, accid):
    # tempalte statement attach to template
    statement = Statement.factory(read_template("{}/templates/policy.statement.json".format(find_directory(__file__))))
    statement.update(sid=sid, accid=accid)
    # tempalte actions allowd
    action = Action.factory(read_template("{}/templates/ecr.action.json".format(find_directory(__file__)))['Action'])
    # attach actions to template
    statement.Action = action.actions
    # enrich template
    template_json.Statement.append(statement)


if __name__ == "__main__" and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from core.utils import deserialize, read_nested, read_template, find_directory


    parser = argparse.ArgumentParser(description='Process Arguments.')
    parser.add_argument('--sharedAccountId', type=str, required=True, dest='account_id')
    parser.add_argument('--repositoryName', type=str, required=True, dest='repository_name')
    parser.add_argument('--principal', type=str, required=True, dest='principal')
    parser.add_argument('--policySid', type=str, required=True, dest='sid')
    parser.add_argument('--region', type=str, required=True, dest='region')
    args = parser.parse_args()

    (esr) = create_context(args.region)

    print("Searching for repository " + args.repository_name)

    try:
        esr.describe_repositories(
            registryId=args.account_id,
            repositoryNames=[
                args.repository_name
            ]
        )
    except:
        raise EnvironmentError("Failed To Find repository.")

    policy = None
    try:
        policy = esr.get_repository_policy(
            registryId=args.account_id,
            repositoryName=args.repository_name
        )
        if "*" in json.dumps(policy['policyText'], default=read_nested()):
            raise EnvironmentError("Policy should not have \'*\'.")
    except:
        pass

    if policy is not None:
        print "Validate/Update policy"
        template = Policy.factory(deserialize(policy['policyText']))
        principals = [re.search(ACCOUNT_NUMBER_PATTERN, stm.Principal['AWS']).group(1) for stm in template.Statement]

        if args.principal in principals:
            print "FOUND ECR Resource based permissions for \'{}\' account.".format(args.principal)
        else:
            __enrich_template(template_json=template, sid=args.sid, accid=args.principal)
            __attach_policy(esr, account_id=args.account_id, repository_name=args.repository_name, template_json=template)

    else:
        print "Policy not found. Attach new Policy"
        template = Policy.factory(read_template("{}/templates/policy.template.json".format(find_directory(__file__))))
        __enrich_template(template_json=template, sid=args.sid, accid=args.principal)
        __attach_policy(esr, account_id=args.account_id, repository_name=args.repository_name, template_json=template)

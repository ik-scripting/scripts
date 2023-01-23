#!/usr/bin/env python
'''
  Find API Gateway. Find keys, Assing them to stage and test against DNS endpoint.
  Usage example
  chmod +x assign_test_key.py
  ./assign_key.py --proxy "pista-android-configuration" \
  --hosted-zone "<project-name>cloud.co.uk" \
  --stage "dev" \
  --prefix "nonprod"
'''

import argparse
import json
import os

parser = argparse.ArgumentParser(description='Process Arguments.')
parser.add_argument('--proxy', type=str, required=True, dest='proxy')
parser.add_argument('--hosted-zone', type=str, required=True, dest='hosted_zone')
parser.add_argument('--stage', type=str, required=True, dest='stage')
parser.add_argument('--prefix', type=str, required=True, dest='prefix')

KEY_TYPE = "API_KEY"


if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from core.session import Session
    from core.utils import prettify

    args = parser.parse_args()
    proxy = args.proxy
    hosted_zone = args.hosted_zone
    stage = args.stage
    prefix = args.prefix

    session = Session.factory()
    gateway_client = session.current.client('apigateway')

    usage_plans = gateway_client.get_usage_plans()
    usage_plan_id = None
    api_id = None
    for plan in usage_plans['items']:
        if plan['name'] == "{}.{}".format(proxy, stage):
            print("Found Usage Plan\n{}".format(prettify(plan)))
            usage_plan_id = plan['id']
            api_id = plan['apiStages'][0]['apiId']

    if usage_plan_id is not None and api_id is not None:
        assigned_keys = gateway_client.get_usage_plan_keys(
            usagePlanId=usage_plan_id
        )
        list_of_assigned_keys = [item['id'] for item in assigned_keys['items']]
        api_keys = gateway_client.get_api_keys(
            nameQuery="{}.{}".format(proxy, prefix),
            includeValues=True)

        for key in api_keys['items']:
            # print("Key\n{}".format(prettify(key)))
            key_value = key['value']
            key_id = key['id']
            if key_id not in list_of_assigned_keys:
                try:
                    assign_key = gateway_client.create_usage_plan_key(
                        usagePlanId=usage_plan_id,
                        keyId = key['id'],
                        keyType = KEY_TYPE
                    )
                    print("Assign Key {} to: \n{}".format(key['id'], prettify(assign_key)))
                except Exception as e:
                    print(e.message)

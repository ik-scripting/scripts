#!/usr/bin/env python

'''
  Create/Update Route 53 Records
  Support updating record sets for aws hosted endpoints


  Usage example:
   export AWS_DEFAULT_REGION=eu-west-1

  ./update_route_53_records.py \
  --dnsName <project-name>cloud.co.uk. \
  --subDomain api.dev \
  --endpointUrl https://myloadbalancer/myapp \
  --updateDnsZone public
'''

import argparse

parser = argparse.ArgumentParser(description='Process Arguments.')
parser.add_argument('--dnsName', type=str, required=True, dest='dns_name')
parser.add_argument('--subDomain', type=str, required=True, dest='subdomain')
parser.add_argument('--endpointUrl', type=str, required=True, dest='endpoint')
parser.add_argument('--updateDnsZone', type=str, required=False, dest='update_dns_zone', default='public')

if __name__ == '__main__' and __package__ is None:
    from os import sys, path, environ

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from py.core.session import Session
    from py.r53.record_sets import update_record_sets

    args = parser.parse_args()

    session = Session.factory()

    dns_info = {
        'domain': args.dns_name,
        'subdomain': args.subdomain,
        'endpoint': args.endpoint,
        'update_public_zones': args.update_dns_zone
    }

    update_record_sets(dns_info=dns_info, session=session)

#!/usr/bin/env python
'''
  Find API Gateway custom domain name URL endpoint
  Usage example
  chmod +x find_domain_url.py
  export URL=$(./find_domain_url.py --get-domain-name "pista-android-configuration.dev.<project-name>cloud.co.uk")
'''

import argparse
import json
import os

parser = argparse.ArgumentParser(description='Process Arguments.')
parser.add_argument('--get-domain-name', type=str,   required=True, dest='domain_name')

def find_value():
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from core.session import Session
    from core.utils import prettify, enablePrint, blockPrint

    blockPrint()
    args = parser.parse_args()
    domain_name = args.domain_name

    session = Session.factory()
    gateway_client = session.current.client('apigateway')
    enablePrint()
    domains = gateway_client.get_domain_names()

    for domain in domains['items']:
        if domain['domainName'] == domain_name:
            print(domain['regionalDomainName'])
            foundDomain = True
            break


if __name__ == '__main__' and __package__ is None:
    find_value()




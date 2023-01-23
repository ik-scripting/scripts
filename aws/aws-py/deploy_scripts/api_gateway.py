#!/usr/bin/env python


import argparse
import json

'''
  Create Update API Gateway Domain Name.
  Support deploy different version of application and configuration.

  Usage example
  chmod +x api_gateway.py
  ./api_gateway.py --domainName 'dev.<project-name>cloud.co.uk' --apiDomainPrefix 'pista' --stage 'dev' \
  --apiName 'pista-android-configuration-dev'
'''

parser = argparse.ArgumentParser(description='Process Arguments.')
parser.add_argument('--domainName', type=str, required=True, dest='domain_name')
parser.add_argument('--apiDomainPrefix', type=str, required=True, dest='api_domain_prefix')
parser.add_argument('--stage', type=str, required=True, dest='stage')
parser.add_argument('--apiName', type=str, required=True, dest='api_name')
parser.add_argument('--basePath', type=str, required=False, dest='base_path', default='')

DOMAIN_PREFIX='*.'


def __create_path_mappings(api_domain_name, base_path, api_id, stage):
    create_path = gateway_client.create_base_path_mapping(
        domainName=api_domain_name,
        basePath=base_path,
        restApiId=api_id,
        stage=stage
    )
    print("Create path mappings\n{}".format(prettify(create_path)))


if __name__ == "__main__" and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from py.core.session import Session
    from py.core.utils import prettify

    args = parser.parse_args()
    domain_name = args.domain_name
    api_domain_prefix = args.api_domain_prefix
    api_name = args.api_name
    stage = args.stage
    base_path = args.base_path
    api_domain_name = "{}.{}".format(api_domain_prefix, domain_name)

    session = Session.factory()
    gateway_client = session.current.client('apigateway')
    acm = session.current.client('acm')

    try:
        apis = gateway_client.get_rest_apis()
        api_id = None
        for api in apis['items']:
            if api['name'] == api_name:
                api_id = api['id']
                print("Found API \n{}".format(prettify(api)))
                break

        if api_id is None:
            print('API endpoint not found')
            exit(1)

        certificates = acm.list_certificates()
        print("Found Certificates \n{}".format(prettify(certificates['CertificateSummaryList'])))
        certificate_arn = None
        certificate_name = None
        for certificate in certificates['CertificateSummaryList']:
            if certificate['DomainName'] == DOMAIN_PREFIX + domain_name:
                print("Found Certificate\n{}".format(prettify(certificate)))
                certificate_arn = certificate['CertificateArn']
                certificate_name = certificate['DomainName']
                break

        if certificate_arn == None:
            print('Certificate not found for\n{}'.format(domain_name))
            exit(1)

        domains = gateway_client.get_domain_names()
        foundDomain = False
        for domain in domains['items']:
            if domain['domainName'] == api_domain_name:
                print("Found Domain\n{}".format(prettify(domain)))
                foundDomain = True
                break

        if not foundDomain:
            create_domain = gateway_client.create_domain_name(
                domainName=api_domain_name,
                regionalCertificateName= certificate_name,
                regionalCertificateArn= certificate_arn,
                endpointConfiguration={
                    'types': [
                        'REGIONAL'
                    ]
                }
            )

            foundDomain = True
            print("Domain not found. Create new domain\n{}".format(prettify(create_domain)))
        try:
            path_mappings = gateway_client.get_base_path_mappings(
                domainName=api_domain_name
            )
            if path_mappings['items']:
                print("Found Base path mappings\n{}".format(prettify(path_mappings['items'])))
            else:
                __create_path_mappings(api_domain_name, base_path, api_id, stage)
        except Exception as e:
            __create_path_mappings(api_domain_name, base_path, api_id, stage)

    except Exception as e:
        print("Failed to execute against an api gateway {}".format(e))
        exit(1)

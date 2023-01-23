#!/usr/bin/env python

import json

from py.core.utils import read_template, find_directory
from py.core.logging import log_debug, log_info


def __update_route_53_records(dns_info, session):
    route53_client = session.current.client('route53')

    domain = dns_info['domain']
    subdomain = dns_info['subdomain']
    endpoint = dns_info['endpoint']

    if dns_info['update_public_zones'] == 'public':
        update_public_zones = True
    else:
        update_public_zones = False

    log_info("Searching for route 53 hosted zones by dns name '{}'".format(domain))

    response = route53_client.list_hosted_zones_by_name(
        DNSName=domain
    )

    for hosted_zone in response['HostedZones']:

        hosted_zone_id = hosted_zone['Id']
        hosted_zone_name = hosted_zone['Name']

        # always update everything if updating public dns
        # otherwise update only private dns
        if update_public_zones is True or hosted_zone['Config']['PrivateZone'] is True:

            log_info("Searching hosted zone with id '{} and name {}'".format(hosted_zone_id, hosted_zone_name))

            # skip updating zones we don't want
            if hosted_zone_name == domain:

                # create the final domain name to be updated
                domain_name = "{}.{}".format(subdomain, domain)

                (hosted_zone_id, found_record_set_name, found_record_set_value) = __check_dns_record_sets(
                    client=route53_client,
                    hosted_zone_id=hosted_zone_id,
                    record_set_name=domain_name,
                    endpoint=endpoint
                )

                if not found_record_set_name or not found_record_set_value:
                    __update_dns_record_sets(
                        client=route53_client,
                        hosted_zone_id=hosted_zone_id,
                        rs_update={
                            "domain_name": domain_name,
                            "endpoint": endpoint
                        }
                    )


def __update_dns_record_sets(client, hosted_zone_id, rs_update):
    endpoint = rs_update['endpoint']
    domain_name = rs_update['domain_name']

    change_batch = read_template("{}/templates/r53.changebatch.json".format(find_directory(__file__)))

    changes = change_batch['Changes']
    change = changes[0]

    resource_rs = change['ResourceRecordSet']

    resource_rs['Name'] = str(resource_rs['Name']).format(domain_name=domain_name)
    resource_records = resource_rs['ResourceRecords']
    resource_rec = resource_records[0]
    resource_rec['Value'] = str(resource_rec['Value']).format(end_domain=endpoint)

    log_debug("{} request = {}".format("change_batch", json.dumps(change_batch, indent=4, sort_keys=True, default=str)))

    response = client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch=change_batch
    )
    # REVIEW: Could add a waiter to hold until change is done but it happens very quickly even though
    # DNS takes a while to propegate
    log_debug("{} response = {}".format("change_resource_record_sets",
                                        json.dumps(response, indent=4, sort_keys=True, default=str)))


def __check_dns_record_sets(client, hosted_zone_id, record_set_name, endpoint):
    log_info("Searching hosted zone domain registry for references to our domain name.")

    record_set_type = 'CNAME'

    response = client.list_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        StartRecordName=record_set_name,
        StartRecordType=record_set_type,
        MaxItems='1'
    )

    found_record_set_name = False
    found_record_set_value = False

    for record_set in response['ResourceRecordSets']:
        # Find the record set type we are after
        if record_set_type == record_set['Type'] and record_set_name == record_set['Name']:
            log_info("Found an existing '{}' record set for domain name '{}'.".format(record_set_type, record_set_name))
            found_record_set_name = True
            # There could be a few
            for resource_records in record_set['ResourceRecords']:
                record_value = resource_records['Value']
                log_info("Which has a resource record value '{}'".format(record_value))
                # Check each one against our required url for a match
                if endpoint == record_value:
                    log_info("Which matches our endpoint.".format(endpoint))
                    found_record_set_value = True

    if not found_record_set_name:
        log_info("Didn't find any record sets for {} which means we'll need to create one and point it to '{}'"
                 .format(record_set_name, endpoint))
    else:
        if not found_record_set_value:
            log_info("But it doesn't match our endpoint '{}' so it will be updated.".format(endpoint))
        else:
            log_info("So no work to do.")

    return hosted_zone_id, found_record_set_name, found_record_set_value


def update_record_sets(dns_info, session):
    __update_route_53_records(dns_info=dns_info, session=session)

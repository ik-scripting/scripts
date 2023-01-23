import unittest
import boto3
from moto import mock_route53
from py.r53.record_sets import update_record_sets
from py.core.session import Session
from py.core.logging import set_log_level


class TestUpdateRoute53Records(unittest.TestCase):

    # configure moto mocking framework which mocks boto3 api calls
    def setUp(self):
        region = 'eu-west-1'

        mock = mock_route53()
        mock.start()

        set_log_level(level=None)

        self.route53_mockclient = boto3.client('route53', region_name=region)
        self.mock = mock
        self.domain = 'mockdomain.co.uk.'
        self.region = region
        self.endpoint = 'https://myloadbalancer/myapp'
        self.private_hosted_zone_id = ''
        self.public_hosted_zone_id = ''
        self.session = Session.factory(region=region)

    def tearDown(self):
        self.mock.stop()

    # tests

    def test_create_private_route_53_records_should_only_create_private_record(self):
        # pretend we have one private and one public zone with same domain name
        self.__create_fake_private_hosted_zone()
        self.__create_fake_public_hosted_zone()

        update_record_sets(dns_info={
            'domain': self.domain,
            'subdomain': 'api.dev',
            'endpoint': self.endpoint,
            'update_public_zones': 'private'
        }, session=self.session)

        response = self.__list_dns_records(self.private_hosted_zone_id)
        self.__assert_dns_record_exists(response, "private")

        response = self.__list_dns_records(self.public_hosted_zone_id)
        self.assert_no_dns_record_exists(response, "public")

    def test_create_public_route_53_records_should_create_public_private_records(self):
        # pretend we have one private and one public zone with same domain name
        self.__create_fake_private_hosted_zone()
        self.__create_fake_public_hosted_zone()

        update_record_sets(dns_info={
            'domain': self.domain,
            'subdomain': 'api.dev',
            'endpoint': self.endpoint,
            'update_public_zones': 'public'
        }, session=self.session)

        response = self.__list_dns_records(self.private_hosted_zone_id)
        self.__assert_dns_record_exists(response, "private")

        response = self.__list_dns_records(self.public_hosted_zone_id)
        self.__assert_dns_record_exists(response, "public")

    def test_update_route_53_records_should_update_same_record(self):
        # pretend we have one private and one public zone with same domain name
        self.__create_fake_private_hosted_zone()
        self.__create_fake_public_hosted_zone()

        # update once
        update_record_sets(dns_info={
            'domain': self.domain,
            'subdomain': 'api.dev',
            'endpoint': self.endpoint,
            'update_public_zones': 'public'
        }, session=self.session)

        # update again
        self.endpoint = 'https://myloadbalancer/adifferentapp'

        update_record_sets(dns_info={
            'domain': self.domain,
            'subdomain': 'api.dev',
            'endpoint': self.endpoint,
            'update_public_zones': 'public'
        }, session=self.session)

        response = self.__list_dns_records(self.private_hosted_zone_id)
        self.__assert_dns_record_count(response, 1)
        self.__assert_dns_record_exists(response, "private")

        response = self.__list_dns_records(self.public_hosted_zone_id)
        self.__assert_dns_record_count(response, 1)
        self.__assert_dns_record_exists(response, "public")

    def test_duplicate_route_53_records_should_be_idempotent(self):
        # pretend we have one private and one public zone with same domain name
        self.__create_fake_private_hosted_zone()
        self.__create_fake_public_hosted_zone()

        # update once
        dns_info = {'domain': self.domain,
                    'subdomain': 'api.dev',
                    'endpoint': self.endpoint,
                    'update_public_zones': 'public'
                    }

        # duplicate calls
        update_record_sets(dns_info=dns_info, session=self.session)
        update_record_sets(dns_info=dns_info, session=self.session)

        response = self.__list_dns_records(self.private_hosted_zone_id)
        self.__assert_dns_record_count(response, 1)

        response = self.__list_dns_records(self.public_hosted_zone_id)
        self.__assert_dns_record_count(response, 1)

    # helpers

    def __list_dns_records(self, zone_id):
        response = self.route53_mockclient.list_resource_record_sets(
            HostedZoneId=zone_id,
            StartRecordName='api.dev.mockdomain.co.uk.',
            StartRecordType='CNAME',
            MaxItems='1'
        )
        return response

    def __assert_dns_record_exists(self, response, visibility):
        dns_record = response['ResourceRecordSets'][0]['ResourceRecords'][0]
        self.assertIsNotNone(dns_record, "Should have created a record in the {} DNS".format(visibility))
        self.assertEqual(dns_record['Value'], self.endpoint, "Should have set the correct endpoint for the DNS")

    def assert_no_dns_record_exists(self, response, visibility):
        dns_record = response['ResourceRecordSets']
        self.assertEqual(len(dns_record), 0, "Should not change the {} DNS".format(visibility))

    def __assert_dns_record_count(self, response, count):
        dns_record = response['ResourceRecordSets'][0]['ResourceRecords'][0]
        self.assertEqual(len(dns_record), count)
        return dns_record

    def __create_fake_private_hosted_zone(self):
        response = self.route53_mockclient.create_hosted_zone(
            Name=self.domain,
            VPC={
                'VPCRegion': self.region,
                'VPCId': 'myVpc'
            },
            CallerReference='myCaller',
            HostedZoneConfig={
                'Comment': 'A private hosted zone',
                'PrivateZone': True
            }
        )

        self.private_hosted_zone_id = response['HostedZone']['Id']

    def __create_fake_public_hosted_zone(self):
        response = self.route53_mockclient.create_hosted_zone(
            Name=self.domain,
            VPC={
                'VPCRegion': self.region,
                'VPCId': 'myVpc'
            },
            CallerReference='myCaller',
            HostedZoneConfig={
                'Comment': 'A public hosted zone',
                'PrivateZone': False
            }
        )

        self.public_hosted_zone_id = response['HostedZone']['Id']

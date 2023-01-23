import unittest
import boto3
import sure
from parameterized import parameterized
from botocore.exceptions import ClientError
from moto import mock_elbv2, mock_ec2
from moto.elbv2 import elbv2_backends
from random import randint

from py.elbv2.health_check import target_group_health_status
from py.core.logging import set_log_level


class TestTargetGroupHealth(unittest.TestCase):

    # configure moto mocking framework which mocks boto3 api calls
    def setUp(self):
        self.region = 'eu-west-1'
        set_log_level(level=None)

    def tearDown(self):
        pass

    @mock_elbv2
    def test_should_not_return_health_for_not_registered_target(self):
        conn = boto3.client('elbv2', region_name=self.region)

        target_group = self._create_target_group(conn)
        target_group_arn = target_group['TargetGroups'][0]['TargetGroupArn']
        result = target_group_health_status(conn, target_group_arn)
        result.should.be.empty

    @parameterized.expand([
        (2, 0, {'healthy': 2}),
        (3, 0, {'healthy': 3}),
        (2, 1, {'healthy': 1}),
        (8, 3, {'healthy': 5})
    ])
    @mock_elbv2
    def test_should_return_target_group_health(self, total, unhealthy, result):
        conn = boto3.client('elbv2', region_name=self.region)

        target_group = self._create_target_group(conn)
        target_group_arn = target_group['TargetGroups'][0]['TargetGroupArn']
        value = target_group_health_status(conn, target_group_arn)

        self._register_targets(conn, target_group_arn, total, unhealthy)
        value = target_group_health_status(conn, target_group_arn)
        value.should.equal(result)

    def _create_target_group(self, connection):
        return connection.create_target_group(
            Name='a-target',
            Protocol='HTTP',
            Port=8080,
            VpcId="vpc.id",
            HealthCheckProtocol='HTTP',
            HealthCheckPort='8080',
            HealthCheckPath='/',
            HealthCheckIntervalSeconds=5,
            HealthCheckTimeoutSeconds=5,
            HealthyThresholdCount=5,
            UnhealthyThresholdCount=2,
            Matcher={'HttpCode': '200'})

    @mock_ec2
    def _register_targets(self, connection, target_arn, total, deregistered):
        ec2 = boto3.resource('ec2', region_name=self.region)
        response = ec2.create_instances(
            ImageId='ami-1234abcd',
            MinCount=total,
            MaxCount=total
        )

        healthy_targets = []
        unhealthy_targets = []

        for idx, instance in enumerate(response):
            port = randint(8000, 9000)
            if (idx + 1) > deregistered:
                pass
            else:
                unhealthy_targets.append(
                    {
                        'Id': instance.id,
                        'Port': port
                    }
                )
            healthy_targets.append(
                {
                    'Id': instance.id,
                    'Port': port,
                }
            )

        response = connection.register_targets(
            TargetGroupArn=target_arn,
            Targets=healthy_targets
        )

        response = connection.deregister_targets(
            TargetGroupArn=target_arn,
            Targets=unhealthy_targets
        )
        return response

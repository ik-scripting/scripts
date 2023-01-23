import unittest
import boto3
from botocore.exceptions import ClientError
from moto import mock_elbv2
from moto.elbv2 import elbv2_backends

from py.elbv2.attributes import deregistration_delay
from py.core.logging import set_log_level


class TestReadTargetGroupAttributes(unittest.TestCase):

    # configure moto mocking framework which mocks boto3 api calls
    def setUp(self):
        self.region = 'eu-west-1'
        set_log_level(level=None)

    def tearDown(self):
        pass

    @mock_elbv2
    def test_should_return_default_deregistration_delay(self):
        conn = boto3.client('elbv2', region_name=self.region)
        default_delay = 300

        target_group = self._create_target_group(conn)
        target_group_arn = target_group['TargetGroups'][0]['TargetGroupArn']

        delay = deregistration_delay(conn, target_group_arn)
        self.assertEqual(default_delay, delay, "Default delay: {} when current delay is {}.".format(default_delay, delay))

    @mock_elbv2
    def test_should_throw_exception_when_target_group_not_found(self):
        with self.assertRaises(ClientError):
            conn = boto3.client('elbv2', region_name=self.region)
            delay = deregistration_delay(conn, 'target_group_not_found')

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



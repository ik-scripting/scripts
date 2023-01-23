from os import sys, path, environ

import unittest
import boto3

from moto import mock_elbv2, mock_ec2
from py.elbv2.load_balancer import create_update_targetgroup, create_update_listener_rule
from py.core.utils import read_template, find_directory
from py.core.session import Session
from py.core.logging import set_log_level
from py.core.config import Config
from tests.core.mockExports import MockExports

from py.core.utils import prettify


class TestLoadBalancer(unittest.TestCase):

    # configure moto mocking framework which mocks boto3 api calls
    def setUp(self):
        sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
        region = 'eu-west-1'

        mockelbv2 = mock_elbv2()
        mockelbv2.start()

        mockec2 = mock_ec2()
        mockec2.start()

        set_log_level(level=None)

        self.elbv2_mockclient = boto3.client('elbv2', region_name=region)
        self.ec2_mock = boto3.resource('ec2', region_name=region)
        self.mocks = [mockelbv2, mockec2]
        self.region = region
        self.load_balancer_name = "my-load-balancer"
        self.targetgroup_name = 'my-target-group'
        self.session = Session.factory(region=region)
        self.vpc_id = "vpc123"
        self.listener_path_pattern = "/my-service/v1*"
        self.config = {
            "VpcId": self.vpc_id,
            "PathPattern": self.listener_path_pattern
        }

        self.loadbalancer_arn = None
        self.listener_arn = None

        self.__create_load_balancer()

        self._assert_rules_and_return(expected_count=1)
        self._assert_target_groups_and_return(expected_count=1)
        exports = MockExports()
        self.__config = Config(exports)


    def tearDown(self):
        for mock in self.mocks:
            mock.stop()

    # tests

    def test_create_targetgroup_should_create_a_targetgroup(self):

        template_config = self.create_template_for_target_group()

        create_update_targetgroup(load_balancer_arn=self.loadbalancer_arn,
                                  template_config=template_config,
                                  session=self.session)

        targetgroups = self._assert_target_groups_and_return(expected_count=2)
        self.assertEqual(targetgroups[1]['TargetGroupName'], self.targetgroup_name,
                         "Wrong name assigned to target group")


    # TODO: add support for updating target groups
    def test_update_targetgroup_should_create_a_targetgroup(self):
        pass

    def test_create_listener_rule_should_create_a_rule(self):
        template_config = self._create_template_config_for_rule(version='v1')

        create_update_listener_rule(template_config=template_config,
                                    session=self.session)

        self._assert_rules_and_return(expected_count=2)

    def test_create_listener_rule_handles_multiple_rules(self):

        template_config = self._create_template_config_for_rule(version='v1')
        create_update_listener_rule(template_config=template_config,
                                    session=self.session)

        template_config = self._create_template_config_for_rule(version='v2')
        create_update_listener_rule(template_config=template_config,
                                    session=self.session)

        template_config = self._create_template_config_for_rule(version='v3')
        create_update_listener_rule(template_config=template_config,
                                    session=self.session)

        rules = self._assert_rules_and_return(expected_count=4)

        self._assert_priority_of(rules, rule_index=0, expected_priority=1)
        self._assert_priority_of(rules, rule_index=1, expected_priority=2)
        self._assert_priority_of(rules, rule_index=2, expected_priority=3)
        self._assert_priority_of(rules, rule_index=3, expected_priority="default")

    # helpers

    def _assert_target_groups_and_return(self, expected_count):
        target_groups = self.__describe_targetgroups()
        actual = len(target_groups)
        self.assertEqual(actual, expected_count, "Expected {} target groups but was {}\n{}"
                         .format(expected_count, actual, prettify(target_groups)))
        return target_groups

    def _create_template_config_for_rule(self, version):
        self.config['ProjectName'] = 'my-service'
        self.config['Version'] = '%s' % version

        template_config = self.__config.load_resource_config(
            "{}/sample-listenerrule.conf.json".format(find_directory(__file__)),
            self.config)

        return template_config

    def create_template_for_target_group(self):
        template_config = self.__config.load_resource_config(
            "{}/sample-targetgroup.conf.json".format(find_directory(__file__)),
            self.config)
        return template_config

    def _assert_rules_and_return(self, expected_count):
        rules = self.__describe_rules()
        actual = len(rules)
        self.assertEqual(actual, expected_count, "Expected {} rules but was {}\n{}"
                         .format(expected_count, actual, prettify(rules)))
        return rules

    def _assert_priority_of(self, rules, rule_index, expected_priority):
        actual = str(rules[rule_index]['Priority'])
        expected = str(expected_priority)
        self.assertEqual(expected, actual,
                         "Expected {} priority on rule but was {} \n{}".format(expected, actual, prettify(rules)))

    def __create_load_balancer(self):
        vpc = self.ec2_mock.create_vpc(
            CidrBlock='10.0.0.0/16',
        )

        subnet = vpc.create_subnet(
            AvailabilityZone='eu-west-1a',
            CidrBlock='10.0.0.0/24'
        )
        # TODO: Fix issue with default target group not showing on load balancer
        default_targetgroup_arn = self.elbv2_mockclient.create_target_group(
            Name='default-targetgroup',
            Protocol='HTTP',
            Port=80,
            VpcId=self.vpc_id
        )['TargetGroups'][0]['TargetGroupArn']

        self.loadbalancer_arn = self.elbv2_mockclient.create_load_balancer(
            Name=self.load_balancer_name,
            Subnets=[subnet.id]
        )['LoadBalancers'][0]['LoadBalancerArn']

        listener_arn = self.elbv2_mockclient.create_listener(
            LoadBalancerArn=self.loadbalancer_arn,
            Protocol='HTTP',
            Port=80,
            DefaultActions=[
                {
                    'Type': 'forward',
                    'TargetGroupArn': default_targetgroup_arn
                }
            ]
        )['Listeners'][0]['ListenerArn']

        self.config['LoadBalancerListener'] = listener_arn
        self.config['TargetGroupArn'] = default_targetgroup_arn

        self.listener_arn = listener_arn;

    def __describe_targetgroups(self):
        response = self.elbv2_mockclient.describe_target_groups()

        return response['TargetGroups']

    def __describe_rules(self):
        response = self.elbv2_mockclient.describe_rules(
            ListenerArn=self.listener_arn
        )

        return response['Rules']

from os import sys, path, environ

import unittest
from py.core.utils import find_directory
from py.core.logging import set_log_level
from py.core.config import Config
from tests.core.mockExports import MockExports


class TestConfig(unittest.TestCase):

    # configure moto mocking framework which mocks boto3 api calls
    def setUp(self):
        sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

        set_log_level(level=None)

        exports = MockExports({
            "VpcId": "vpc123",
            "LoadBalancer": "my-load-balancer",
            "LoadBalancerListener": "load-balancer-listener",
            "ClusterArn": "my-cluster"
        })
        self._config = Config(exports)

    def tearDown(self):
        pass


    def test_load_environment_config(self):
        environment_template = self._config.load_environment_dict(env_conf_file="tests/deploy-env/sample.conf.json")

        self._assertEqual(actual=environment_template['ServiceName'], expected='my-service-v1')
        self._assertEqual(actual=environment_template['VpcId'], expected='vpc123')

    def test_load_environment_config_with_profile(self):
        environment_template = self._config.load_environment_dict(env_conf_file="tests/deploy-env/sample.conf.json",
                                                                  profile_config_file="tests/deploy-env/profile.conf.json")

        self._assertEqual(actual=environment_template['ServiceName'], expected='my-service-v1')
        self._assertEqual(actual=environment_template['VpcId'], expected='vpc123')
        self._assertEqual(actual=environment_template['ProjectName'], expected='my-sample-project-v1')
        
    def test_load_resource_config_substitutions(self):

        subs = {
            "StringValue": "abc123",
            "NumberValue": 123
        }

        resource_template = self._config.load_resource_config('tests/core/resource-config.json', subs)

        self._assertEqual(actual=resource_template['stringVal'], expected='abc123')
        self._assertEqual(actual=type(resource_template['numVal']), expected=int)
        self._assertEqual(actual=resource_template['numVal'], expected=123)

    def test_load_resource_config_nested_substitutions(self):

        subs = {
            "StringValue": "abc123",
            "NumberValue": 123,
            "StringNumber": "123"
        }

        resource_template = self._config.load_resource_config('tests/core/resource-config.json', subs)

        nested_item=resource_template['nestVal']['numVal']
        self._assertEqual(actual=type(nested_item), expected=int)
        self._assertEqual(actual=nested_item, expected=123)

        list_item=resource_template['listVal'][0]['numVal']
        self._assertEqual(actual=type(list_item), expected=int)
        self._assertEqual(actual=list_item, expected=123)

        list_item=resource_template['listVal'][0]['numVal2']
        self._assertEqual(actual=type(list_item), expected=int)
        self._assertEqual(actual=list_item, expected=123)

        nested_list_item=resource_template['listVal'][0]['nestVal']['numVal']
        self._assertEqual(actual=type(nested_list_item), expected=int)
        self._assertEqual(actual=nested_list_item, expected=123)

        nested_list_within_list_item=resource_template['listVal'][1]['listVal'][0]
        self._assertEqual(actual=type(nested_list_within_list_item), expected=int)
        self._assertEqual(actual=nested_list_within_list_item, expected=123)

        list_item=resource_template['listVal'][2]['stuffOfThings']['value']
        self._assertEqual(actual=type(list_item), expected=unicode)
        self._assertEqual(actual=list_item, expected="123")



    def _assertEqual(self, actual, expected):
        self.assertEqual(actual, expected, "Expected {} value but was {}".format(expected, actual))

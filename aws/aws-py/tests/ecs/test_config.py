from os import sys, path, environ

import unittest
from py.core.utils import find_directory
from py.core.logging import set_log_level
from py.ecs.config import ClusterConfig
from py.core.utils import read_template
from tests.core.mockExports import MockExports


class TestEcsConfig(unittest.TestCase):

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
        self._config = ClusterConfig(exports)

    def tearDown(self):
        pass

    # tests

    def test_read_remote_cluster_config(self):
    
        remote_deploy_config = self._config.read_remote_cluster_config(config=read_template("tests/deploy-env/cluster.conf.json"), 
                                                      key_name='enterprise-services-ecs-cluster')


        actual = remote_deploy_config['ClusterName']
        expected = 'sample-enterprise-services-ecs-cluster'
        self.assertEqual(actual, expected, "Expected {} value but was {}".format(expected, actual))

        actual = remote_deploy_config['ClusterArn']
        expected = 'my-cluster'
        self.assertEqual(actual, expected, "Expected {} value but was {}".format(expected, actual))
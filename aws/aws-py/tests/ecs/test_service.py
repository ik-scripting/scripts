from os import sys, path, environ

import unittest
import boto3

from moto import mock_ecs
from py.ecs.service import create_update_service
from py.core.utils import read_template, find_directory
from py.core.session import Session
from py.core.logging import set_log_level
from py.ecs.task_def import register_task_def
from py.core.config import Config
from tests.core.mockExports import MockExports


class TestECSService(unittest.TestCase):

    # configure moto mocking framework which mocks boto3 api calls
    def setUp(self):
        sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
        region = 'eu-west-1'

        mock = mock_ecs()
        mock.start()

        set_log_level(level=None)

        self.ecs_mockclient = boto3.client('ecs', region_name=region)
        self.mock = mock
        self.region = region
        self.cluster_name = "my-cluster"
        self.service_name = "my-service-v1-dev"
        self.cluster_arn = None
        self.session = Session.factory(region=region)
        exports = MockExports()
        self._config = Config(exports)


    def tearDown(self):
        self.mock.stop()

    # tests

    def test_create_service_should_create_service_in_ecs(self):
        cluster_arn = self.__create_cluster()
        config = {
            "ClusterArn": cluster_arn,
            "ServiceName": self.service_name
        }

        task_def_config = self._create_template_for_task_def(config)
        register_task_def(template=task_def_config, session=self.session)

        template_config = self._create_template_for_service(config)
        create_update_service(template_config=template_config, session=self.session)

    def _create_template_for_service(self, config):
        template_config = self._config.load_resource_config(
            "{}/sample-service.conf.json".format(find_directory(__file__)), config)
        return template_config

    # helpers

    def __create_cluster(self):
        response = self.ecs_mockclient.create_cluster(
            clusterName=self.cluster_name
        )
        return response['cluster']['clusterArn']

    def __describe_services(self):
        response = self.ecs_mockclient.describe_services(
            cluster=self.clust_name,
            services=[
                self.service_name,
            ]
        )
        print(response)

    def _create_template_for_task_def(self, config):
        return self._config.load_resource_config(
            "{}/sample-ecs-task-def.conf.json".format(find_directory(__file__)), config)

from os import sys, path, environ

import unittest
import boto3

from moto import mock_ecs
from py.ecs.task_def import register_task_def
from py.core.utils import read_template, find_directory
from py.core.session import Session
from py.core.logging import set_log_level
from py.core.config import Config
from tests.core.mockExports import MockExports

from py.core.utils import prettify


class TestRegisterECSTaskDef(unittest.TestCase):

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
        self.session = Session.factory(region=region)
        exports = MockExports()
        self.__config = Config(exports)
        self.task_def_family = 'my-service-v1'
        self.config = {
            "ServiceName": self.task_def_family,
            "MyEnvironmentVar": 'my-environment'
        }

    def tearDown(self):
        self.mock.stop()

    # tests

    def test_register_task_definition_should_create_one(self):
        template = self.__config.load_resource_config(
            "{}/sample-ecs-task-def.conf.json".format(find_directory(__file__)),
            self.config)

        task_def_arn = register_task_def(template=template, session=self.session)

        task_defs = self.__list_task_defs()

        self.assertEqual(len(task_defs['taskDefinitionArns']), 1, "Wrong number of task definitions created")

        task_defs_info = self.__describe_task_defs(task_def_arn)

        expected = self.task_def_family
        actual = task_defs_info['taskDefinition']['family']
        self.assertEqual(expected,
                         actual, "Expected value {} but was {}\n{}".format(expected, actual, prettify(task_defs_info)))

    # helpers

    def __list_task_defs(self):
        response = self.ecs_mockclient.list_task_definitions()
        return response

    def __describe_task_defs(self, task_def_arn):
        response = self.ecs_mockclient.describe_task_definition(
            taskDefinition=task_def_arn
        )
        return response

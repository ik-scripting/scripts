import unittest
import boto3
import sure
from botocore.exceptions import ClientError
from moto import mock_elbv2
from moto.elbv2 import elbv2_backends
import json
from parameterized import parameterized

from py.core.logging import set_log_level
from py.core.utils import find_directory

from py.elbv2.load_balancer import _resolve_priority

class TestPriorityRules(unittest.TestCase):

    @classmethod
    def setUp(self):
        set_log_level(level=None)

    @classmethod
    def tearDown(self):
        pass

    @parameterized.expand([
        ('1xRules', 1),
        ('3xRules', 3),
        ('7xRules', 7),
        ('11xRules', 11),
        ('empty', 1)
    ])
    def test_should_resolve_priority(self, rules, resolved):
        data = json.loads(open(find_directory(__file__) + '/rules.json').read())
        result = _resolve_priority(data[rules]['Rules'])
        result.should.equal(resolved)

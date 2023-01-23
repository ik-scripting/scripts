#!/usr/bin/env python
'''
 Assume the AWS IAM role specified and return a new session for actions under that role.
'''

import os
import boto3

from logging import log_debug, log_info


class Session:
    def __init__(self, region, role_arn=None):

        self.region = region

        if role_arn is None:

            log_info("Creating session using current credentials")
            self.current = boto3.session.Session(region_name=self.region)
        else:
            sts_client = boto3.client('sts')

            log_info("Creating session via sts temporary credentials")

            assumed_role_object = sts_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName="PythonSession"
            )

            # From the response that contains the assumed role, get the temporary
            # credentials that can be used to make subsequent API calls
            credentials = assumed_role_object['Credentials']
            log_debug("--RESOLVE-- {}".format(credentials))
            # Use the temporary credentials that AssumeRole returns to make a
            # connection to Amazon S3
            self.current = boto3.Session(
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken'],
                region_name=region
            )

    @staticmethod
    def factory(region=None, role_arn=None):
        if not region:
            region = os.environ['AWS_DEFAULT_REGION']

        return Session(role_arn=role_arn, region=region)

    def __str__(self):
        return self.__dict__

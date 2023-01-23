#!/usr/bin/env python
'''
  Create Elastic Beanstalk application if it doesn't yet exist
'''
import json

from botocore.exceptions import ClientError
from resources import responses


def __create_application(eb_context):
    response = eb_context.eb_client.create_application(
        ApplicationName=eb_context.application,
        Description='Boto3 Make application',
        ResourceLifecycleConfig={
            'ServiceRole': eb_context.beanstalk_service_role,
            'VersionLifecycleConfig': {
                'MaxCountRule': {
                    'Enabled': True,
                    'MaxCount': 123,
                    'DeleteSourceFromS3': True
                }
            }
        }
    )

    return response


def make_application(eb_context):
    try:
        response = __create_application(eb_context)
        print(json.dumps(response, indent=4, sort_keys=True, default=str))

    except ClientError as ex:
        string = responses['app.exists'].replace('{app-name}', eb_context.application)
        if string in ex.message:
            print("Application already exists.")
        else:
            print("ex.message " + ex.message)
            raise ex

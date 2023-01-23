#!/usr/bin/env python
'''
  Create/Update Elastic BeanStalk Environment.
  Support deploy different version of application and configuration.
'''

import json

from status_check import wait_for_app_ready


def __create_environment(environment, tags_file, template, eb_context):
    if tags_file is not None:
        tags = json.loads(open(tags_file).read())
    else:
        tags = ""

    response = eb_context.eb_client.create_environment(
        ApplicationName=eb_context.application,
        EnvironmentName=environment,
        Description='Service Created with CI',
        Tier={
            'Name': 'WebServer',
            'Type': 'Standard'
        },
        Tags=tags,
        VersionLabel=eb_context.version,
        TemplateName=template
    )

    print(json.dumps(response, indent=4, sort_keys=True, default=str))

    try:
        wait_for_app_ready(environment=environment, eb_context=eb_context)
    except EnvironmentError as e:
        print str(e)
        raise EnvironmentError("Failed To Create Environment. Manual Action required.")


def __update_environment(environment, template, eb_context):
    response = eb_context.eb_client.update_environment(
        ApplicationName=eb_context.application,
        EnvironmentName=environment,
        VersionLabel=eb_context.version,
        TemplateName=template
    )

    print(json.dumps(response, indent=4, sort_keys=True, default=str))

    try:
        wait_for_app_ready(environment=environment, eb_context=eb_context)
    except EnvironmentError as e:
        print str(e)
        raise EnvironmentError("Failed To Update Environment. Manual Rollback required.")


def make_environment(environment, template, eb_context, tags_file=None):
    response = eb_context.eb_client.describe_environments(
        ApplicationName=eb_context.application,
        EnvironmentNames=[
            environment,
        ],
        IncludeDeleted=False
    )

    if response['Environments']:
        print 'Found Environment. Updating...'
        __update_environment(environment=environment, template=template, eb_context=eb_context)
    else:
        print 'Not Found Environment. Creating...'
        __create_environment(environment=environment, tags_file=tags_file, template=template, eb_context=eb_context)

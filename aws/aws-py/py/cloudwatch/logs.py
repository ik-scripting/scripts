#!/usr/bin/env python

from py.core.utils import prettify
from py.core.logging import log_debug, log_info

HTTP_OK = 200


def create_update_log_group(group_name, session):
    return __create_update_log_group(group_name=group_name, session=session)


# no update yet
def __create_update_log_group(group_name, session):
    log_info("===============================")
    log_info("Create & Update Log group...")
    log_info("===============================")

    logs_client = session.current.client('logs')

    response = logs_client.describe_log_groups(
        logGroupNamePrefix=group_name
    )

    if response['ResponseMetadata']['HTTPStatusCode'] != HTTP_OK:
        error = "Error fetching Log group information"
        raise EnvironmentError(error)

    if response['ResponseMetadata']['HTTPStatusCode'] == HTTP_OK:
        for log_group in response['logGroups']:
            if log_group['logGroupName'] == group_name:
                log_info('Log Group Already exists')
                return

    response = logs_client.create_log_group(
        logGroupName=group_name
    )

    log_debug(prettify(response))

    if response['ResponseMetadata']['HTTPStatusCode'] != HTTP_OK:
        error = "Error creating Log group"
        raise EnvironmentError(error)

    log_info("===========================")
    log_info("Finished Creating & updating Log groups.")
    log_info("===========================")

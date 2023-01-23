#!/usr/bin/env python
'''
  Module describe attribute for a specific target group
'''

from py.core.logging import log_info

DELAY = 300

def deregistration_delay(client, target_group):
    """
     Lookup for specified target group deregistration delay.
     If delay cannot be found, it set to constant value.
    """
    log_info("=============================================")
    log_info("Deregistration delay is currently defaulted to 120 seconds")
    log_info("The Deregistration Delay can be set manually.")
    log_info("Login to AWS console. EC2. Find right Target Group.")
    log_info("Descrpiption > Attributes > Edit Attributes")
    log_info("=============================================")

    target_attributes = client.describe_target_group_attributes(
        TargetGroupArn=target_group
    )

    deregistration_delay = None

    for attribute in target_attributes['Attributes']:
        if attribute['Key'] == 'deregistration_delay.timeout_seconds':
            deregistration_delay = int(attribute['Value'])
            break

    if deregistration_delay is not None:
        pass
    else:
        deregistration_delay = DELAY

    return deregistration_delay

#!/usr/bin/env python
'''
  Module contains information about health of the various targets
'''

from py.core.logging import log_info

HEALTHY = 'healthy'
EMPTY = 0
ONE = 1

def target_group_health_status(client, target_group):
    """Helth check lookups for given target group."""

    targets = client.describe_target_health(
        TargetGroupArn=target_group
    )

    log_info("Found `{}` targets.".format(len(targets['TargetHealthDescriptions'])))
    result = {}
    for target in targets['TargetHealthDescriptions']:
        state = target['TargetHealth']['State']
        port = target['Target']['Port']
        if state == HEALTHY:
            log_info('State: `{}`. Port: `{}`.'.format(state, port))
        else:
            description = target['TargetHealth']['Description']
            log_info('State: `{}`. Port: `{}`. Description: `{}`'.format(state, port, description))
        result[state] = result.get(state, EMPTY) + ONE

    return result

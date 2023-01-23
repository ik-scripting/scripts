#!/usr/bin/env python

from py.core.utils import read_template, prettify, deserialize
from py.core.logging import log_debug, log_info

HTTP_OK = 200
DEREGISTRATION_DELAY = 'deregistration_delay.timeout_seconds'
TWO_MINUTES = str(2 * 60)
ONE = 1

def create_update_targetgroup(load_balancer_arn, template_config, session):
    return __create_update_targetgroup(load_balancer_arn, template=template_config, session=session)


def create_update_listener_rule(template_config, session):
    return __create_update_listener_rule(template=template_config, session=session)


# no update yet
def __create_update_listener_rule(template, session):
    log_info("===========================")
    log_info("Create & Update Rule...")
    log_info("===========================")

    elbv2_client = session.current.client('elbv2')

    response = elbv2_client.describe_rules(ListenerArn=template['ListenerArn'])

    status = response['ResponseMetadata']['HTTPStatusCode']

    # if listener already exists then nothing to do - updates not supported
    if status == HTTP_OK and len(response['Rules']) > 0:
        for rule in response['Rules']:
            if len(rule['Conditions']) > 0 and len(rule['Conditions'][0]['Values']) > 0 and \
                rule['Conditions'][0]['Values'][0] == template['Conditions'][0]['Values'][0]:
                log_debug("Found Listener Rule {}".format(prettify(response)))
                return

    log_debug(prettify(response))

    status = response['ResponseMetadata']['HTTPStatusCode']

    if status == HTTP_OK:
        rules = response['Rules']
        priority = _resolve_priority(rules)
        template['Priority'] = priority
        log_debug("Setting load balancer rule priority {}".format(priority))

    response = elbv2_client.create_rule(**template)

    if response['ResponseMetadata']['HTTPStatusCode'] == HTTP_OK:
        log_info("Create New Listener Rule {}".format(prettify(response)))
    else:
        error = "Error registering new Rule"
        raise EnvironmentError(error)

    return response['Rules'][0]['RuleArn']

def _resolve_priority(rules):
    """Read rules, sort them into descending order and resolve current rule"""
    sorted_rules = _sort_by_priority_ignore_default(rules)
    priority = ONE
    if sorted_rules:
        priority = int(sorted_rules[0]['Priority']) + ONE
    return priority

def _sort_by_priority_ignore_default(rules):
    """Sort rules in descending numerical order"""
    sorted_rules = sorted(filter(lambda k: k['Priority'] != 'default', rules), key=lambda k: int(k['Priority']),
                          reverse=True)
    return sorted_rules

def _modify_deregistration_delay(client, arn):
    """Update deregistration delay"""
    client.modify_target_group_attributes(
        TargetGroupArn=arn,
        Attributes=[
            {
                'Key': DEREGISTRATION_DELAY,
                'Value': TWO_MINUTES
            }
        ]
    )


# no update yet
def __create_update_targetgroup(load_balancer_arn, template, session):
    log_info("===============================")
    log_info("Create & Update target group...")
    log_info("===============================")

    elbv2_client = session.current.client('elbv2')

    response = elbv2_client.describe_target_groups(
        LoadBalancerArn=load_balancer_arn
    )

    log_debug("OK describe_target_groups")

    if response['ResponseMetadata']['HTTPStatusCode'] == HTTP_OK:
        for group in response['TargetGroups']:
            if group['TargetGroupName'] == template['Name']:
                print("Found Target Group {}".format(prettify(group)))
                _modify_deregistration_delay(elbv2_client, group['TargetGroupArn'])
                return group['TargetGroupArn']

    log_debug("targetGroupTemplate: {}".format(prettify(template)))

    response = elbv2_client.create_target_group(**template)

    log_debug("OK create_target_group")

    if response['ResponseMetadata']['HTTPStatusCode'] is not HTTP_OK:
        raise EnvironmentError("Error registering Target Group")

    target_group_arn = response['TargetGroups'][0]['TargetGroupArn']
    _modify_deregistration_delay(elbv2_client, target_group_arn)

    log_info("Create New Target Group {}".format(prettify(response)))
    return target_group_arn

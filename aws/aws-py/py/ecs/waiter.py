#!/usr/bin/env python
'''
 Provide Health Check status of current instance for current target group.
 Make a health check status call on behalf of client.
'''
import time

from py.core.utils import prettify
from py.core.decorators import log_entry_and_exit
from py.core.logging import log_info
from py.elbv2.health_check import target_group_health_status
from py.elbv2.attributes import deregistration_delay
from py.ecs.resources import WAITERMSG

ONE_MINUTE = 60
ONE = 1
HEALTHY = 'healthy'
WAIT_TIME = 20
EMPTY = 0
FIRST = 0
PRIMARY_TASK = 'PRIMARY'

@log_entry_and_exit
def _task_status(session, cluster, service, task):
    '''
     Validate whehter or not specified task is currently running.
     Supports only one running task at the moment.
     Only one service is supported as well.
     The method validates where or not current task has ACTIVE state.
    '''

    ecs_client = session.current.client('ecs')

    service_describe = ecs_client.describe_services(
        cluster=cluster,
        services=[
            service
        ]
    )

    if len(service_describe['failures']) > EMPTY:
        log_info("Failures {}".format(prettify(service_describe['failures'])))

    allowed_sick_time = ONE_MINUTE
    timetowait = WAIT_TIME
    sick_time = EMPTY

    while True:
        time.sleep(WAIT_TIME)
        flag = False
        for deployment in service_describe['services'][FIRST]['deployments']:
            task_definition = deployment['taskDefinition']
            status = deployment['status']
            log_info(WAITERMSG['taskstatus'].format(status, task_definition))
            if task_definition == task and status == PRIMARY_TASK:
                flag = True

        if flag:
            log_info(WAITERMSG['taskrunning'].format(task.split("/")[-1]))
            break
        elif sick_time >= allowed_sick_time:
            raise EnvironmentError(
                prettify(service_describe['services'][FIRST]['deployments']))
        sick_time += timetowait


@log_entry_and_exit
def _target_health_status(session, target_group, desired_count):
    """
     Validate Health Check for specified target group.
    """
    elbv2 = session.current.client('elbv2')
    # how much time is environment unstable before we give up
    delay = deregistration_delay(elbv2, target_group)
    allowed_sick_time = 2 * delay

    log_info(WAITERMSG['deregistration'].format(delay))
    log_info(WAITERMSG['message'])

    timetowait = WAIT_TIME
    sick_time = EMPTY

    while True:
        time.sleep(WAIT_TIME)

        count_state = target_group_health_status(elbv2, target_group)

        log_info(WAITERMSG['recovertime'].format(allowed_sick_time - sick_time))
        log_info(WAITERMSG['state'].format(count_state))

        if sick_time >= allowed_sick_time:
            if _validate_healthy_targets(count_state=count_state, desired_count=desired_count):
                log_info(WAITERMSG['inconsistent'].format(count_state))
                break
            else:
                error = WAITERMSG['failed'].format(count_state, HEALTHY, desired_count)
                raise EnvironmentError(error)
        elif _is_deployment_suceed(count_state=count_state, desired_count=desired_count, sick_time=sick_time):
            log_info(WAITERMSG['complete'].format(HEALTHY, count_state.get(HEALTHY)))
            break

        sick_time += timetowait

def _validate_healthy_targets(count_state, desired_count):
    "Check whehter registered targets have a correct number of healthy instances"
    return HEALTHY in count_state and count_state.get(HEALTHY) == desired_count

def _is_deployment_suceed(count_state, desired_count, sick_time):
    "Validate whether or not deployment is completed"
    return len(count_state) == ONE and HEALTHY in count_state and sick_time > ONE_MINUTE and count_state.get(HEALTHY) == desired_count


def _show_events(session, cluster, service):
    log_info("==================== EVENT MESSAGES start ====================")
    ecs_client = session.current.client('ecs')

    service_describe = ecs_client.describe_services(
        cluster=cluster,
        services=[
            service
        ]
    )
    for event in service_describe['services'][FIRST]['events']:
        log_info(" {}".format(event['message']))
    log_info("==================== EVENT MESSAGES end ====================")


def waiter(session, cluster, service, task, target_group, desired_count):
    '''
       Polls every 20 seconds untill a successful state is reached for health check
        and task registration.
       Health Chechk validator with Task Check Validator.
       If healtcheck fails, it does not validates whether or not specified task is
        in running state.
    '''
    try:
        _target_health_status(session=session, target_group=target_group, desired_count=desired_count)
        _task_status(session=session, cluster=cluster, service=service, task=task)
    except Exception as e:
        log_info(WAITERMSG['validationfailed'])
        _show_events(session, cluster, service)
        raise EnvironmentError(e.message)

#!/usr/bin/env python
'''
 Check the application environment status.
'''
import time

from call_service import call_service
from show_events import show_events


def __retrieve_health_endpoint(environment, eb_context):
    '''
    Find health check endpoint
    :return: healthcheck endpoint
    '''
    response = eb_context.eb_client.describe_configuration_settings(
        ApplicationName=eb_context.application,
        EnvironmentName=environment
    )
    return next(endpoint['Value'] for endpoint in response['ConfigurationSettings'][0]['OptionSettings'] if
                endpoint['OptionName'] == 'HealthCheckPath')


def __execute(environment, eb_context):
    response = eb_context.eb_client.describe_environments(
        ApplicationName=eb_context.application,
        EnvironmentNames=[
            environment,
        ],
        IncludeDeleted=False
    )

    test_app = {'health_app': 'no CNAME found', 'status_app': 'no CNAME found'}
    try:
        if response['Environments'] and response['Environments'][0] and 'CNAME' in response['Environments'][0]:
            test_app = call_service(
                'https://{}{}'.format(response['Environments'][0]['CNAME'],
                                      __retrieve_health_endpoint(environment, eb_context)))
    except Exception as e:
        pass

    health = response['Environments'][0]['Health'] if response['Environments'] else ''
    status = response['Environments'][0]['Status'] if response['Environments'] else ''
    return {'health_env': health, 'status_env': status, 'health_app': test_app['health_app'],
            'status_app': test_app['status_app']}


def wait_for_app_ready(environment, eb_context):

    timetowait = 20
    allowed_sick_time = 300  # how much time is environment unstable before we give up

    sick_time = 0

    while True:
        time.sleep(timetowait)
        check = __execute(environment=environment, eb_context=eb_context)
        status = check['status_env']
        health = check['health_env']

        print "Environment Status --{}-- and Health --{}--. Health Check Status --{}-- and Response --{}--" \
            .format(status, health, check['status_app'], check['health_app'])

        if status == 'Ready' and health == 'Green':
            print "Accept status --{}-- and health --{}-- as successful deployment!".format(status, health)
            break
        elif health in {'Yellow', 'Red'} or (status == 'Ready' and health == 'Grey'):
            show_events(environment=environment, eventtype='WARN', seconds=timetowait, eb_context=eb_context)

            if sick_time > allowed_sick_time:
                error = "Failed Deploy New Configuration. Health {}. Status {}".format(health, status)
                raise EnvironmentError(error)

            print "Health {}. Status {}".format(health, status)
            print "Allowing {} seconds of time to recover...".format(allowed_sick_time - sick_time)
            sick_time += timetowait

#!/usr/bin/env python

from py.core.utils import prettify
from py.core.decorators import log_entry_and_exit
from py.core.logging import log_debug, log_info

HTTP_OK = 200

@log_entry_and_exit
def __create_update_service(template, session):
    log_info("======================")
    log_info("Registering Service with ECS...")
    log_info("======================")

    ecs_client = session.current.client('ecs')

    response = ecs_client.describe_services(
        cluster=template['cluster'],
        services=[
            template['serviceName'],
        ]
    )

    if response['ResponseMetadata']['HTTPStatusCode'] == HTTP_OK and _is_service_active(response['services']):

        log_debug("Found Service {}".format(prettify(response)))

        for service in response['services']:
            if service['status'] in ['INACTIVE', 'DRAINING']:
                pass
            else:
                log_info("===========================")
                log_info("Updating existing service...")
                log_info("===========================")

                # handle inconsistent API in boto 3 for create / update service
                template['service'] = template['serviceName']
                del template['serviceName']
                del template['loadBalancers']
                del template['role']

                template['desiredCount'] = int(template['desiredCount'])

                log_info("Update Service template {}".format(prettify(template)))

                response = ecs_client.update_service(**template)

                del response['service']['events']
                log_info("===========================")
                log_info("Finished updating service... {}".format(prettify(response)))
                log_info("===========================")
                return

    log_info("===========================")
    log_info("Creating new service...")
    log_info("===========================")

    log_info("Create Service template {}".format(prettify(template)))

    response = ecs_client.create_service(**template)

    if response['ResponseMetadata']['HTTPStatusCode'] != HTTP_OK:
        error = "Error registering Service"
        raise EnvironmentError(error)

    del response['service']['events']
    log_info("===========================")
    log_info("Finished creating new service. {}".format(prettify(response)))
    log_info("===========================")


def _is_service_active(services):
    for service in services:
        status = service['status']
        if status == 'ACTIVE':
            return True
    return False


def create_update_service(template_config, session):
    return __create_update_service(template=template_config, session=session)

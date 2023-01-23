#!/usr/bin/env python
'''
 Register task definition with template provided.
'''

import json

from py.core.utils import prettify
from py.core.logging import log_debug, log_info


def __register_task_def(template, session):
    log_info("======================================")
    log_info("Registering task definition with ECS..")
    log_info("======================================")
    log_info(".")
    ecs_client = session.current.client('ecs')

    log_debug(
        "{} = {}".format("register task definition request", json.dumps(template, indent=4, sort_keys=False)))

    try:
        response = ecs_client.register_task_definition(**template)

        log_info("=====================================")
        log_info("Finished registering task definition... {}".format(prettify(response)))
        log_info("======================================")

        # return identifier of task definition
        arn = response['taskDefinition']['taskDefinitionArn']
        return arn

    except Exception as e:
        raise EnvironmentError("Failed set task definition {}".format(e.message))


def register_task_def(template, session):
    return __register_task_def(template=template, session=session)

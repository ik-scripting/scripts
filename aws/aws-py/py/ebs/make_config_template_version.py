#!/usr/bin/env python
'''
  Create Elastic BeanStalk Application Configuration template
'''

import json


def __delete_configuration_template(eb_context, environment):
    response = eb_context.eb_client.delete_configuration_template(
        ApplicationName=eb_context.application,
        TemplateName="{}:{}".format(environment, eb_context.version)
    )

    return response


def __create_versioned_configuration_template(environment, env_options, solution_conf_file, eb_context):

    solution_stack_name = open(solution_conf_file).read()
    print("Configuration added \n{}".format(json.dumps(env_options, indent=4, sort_keys=True, default=str)))

    template_name = "{}:{}".format(environment, eb_context.version)
    response = eb_context.eb_client.create_configuration_template(
        ApplicationName=eb_context.application,
        TemplateName=template_name,
        Description='Template created from the CI using "boto3"',
        SolutionStackName=solution_stack_name,
        OptionSettings=env_options
    )
    print("Create Configuration Template".format(environment, eb_context.version))

    print(json.dumps(response, indent=4, sort_keys=True, default=str))


def __delete_duplicate_version(environment, eb_context):
    try:
        __delete_configuration_template(eb_context=eb_context, environment=environment)
    except Exception:
        print 'No template found to delete'
        pass


def make_config_version(environment, env_options, solution_conf_file, eb_context):
    __delete_duplicate_version(environment=environment, eb_context=eb_context)
    __create_versioned_configuration_template(environment=environment,
                                              env_options=env_options,
                                              solution_conf_file=solution_conf_file,
                                              eb_context=eb_context
                                             )

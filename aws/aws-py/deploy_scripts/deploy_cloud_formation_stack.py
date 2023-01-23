#!/usr/bin/env python

import argparse

parser = argparse.ArgumentParser(description='Process Arguments.')
parser.add_argument('--envConfFile', type=str, required=True, dest='config_file')
parser.add_argument('--templateFile', type=str, required=True, dest='template_file')
parser.add_argument('--stackName', type=str, required=True, dest='stack_name')
parser.add_argument('--region', type=str, required=False, dest='region', default=None)
parser.add_argument('--buildParams', type=str, required=False, nargs='*', dest='build_params',
                    help='Optional parameters. Usage: e.g. \"Key1=Value\" \"Key2=Value\".')
parser.add_argument('--paramExportOverride', type=str, required=False, nargs='*', dest='param_exp_override',
                    help='Optional parameters. Used to export values. Usage: e.g. \"Key1=Value\" \"Key2=Value\".')
parser.add_argument('--capabilities', type=str, required=False, nargs='*', dest='capabilities',
                    help='Optional parameters. Capabilities e.g. "CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"')

def __deploy_stack(stack_info, cf_client):

    deployer = Deployer(cf_client)
    print("Deploying cloudformation stack '{}'".format(stack_info['stack_name']))
    print("Using parameters \n{}".format(prettify(stack_info['parameters'])))

    if not path.isfile(stack_info['template_file']):
        raise InvalidTemplatePathError(
            template_path=stack_info['template_file'])

    with open(stack_info['template_file'], "r") as handle:
        template_str = handle.read()

    try:
        result = deployer.create_and_wait_for_changeset(
            stack_name=stack_info['stack_name'],
            cfn_template=template_str,
            parameter_values=stack_info['parameters'],
            capabilities=stack_info['capabilities'])

        # print result

        deployer.execute_changeset(result.changeset_id, stack_info['stack_name'])
        deployer.wait_for_execute(stack_info['stack_name'], result.changeset_type)

        print("Cloudformation stack deployed successfully.")

    except ChangeEmptyError:
        print("No changes detected in stack - nothing to do.")


def __load_cloudformation_config(env_conf_file, optinal_params, config):
    mandatory_options = config.load_environment_config(env_conf_file=env_conf_file, profile_config_file=None)
    env_options = config.merge_optional_config(mandatory_options=mandatory_options, optional_options=optinal_params)
    # swap the names over
    for option in env_options:
        if 'Value' in option:
            value = option['Value']
            option.pop('Value', None)
            option['ParameterValue'] = value

    return env_options


if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from py.core.session import Session
    from py.core.config import Config
    from py.core.exports import Exports
    from py.core.utils import prettify
    from py.cft.deployer import Deployer
    from py.cft.errors import ChangeEmptyError, InvalidTemplatePathError

    args = parser.parse_args()
    session = Session.factory()
    config = Config(Exports(session))

    # Merge optional values if any
    paramsOverride = []
    if args.build_params:
        paramsOverride = list(
            {'ParameterKey': k.split('=')[0], 'ParameterValue': k.split('=')[1]} for k in args.build_params)
    paramsExportOverride = []
    if args.param_exp_override:
        paramsExportOverride = list(
            {'ParameterKey': k.split('=')[0], 'ExportName': k.split('=')[1]} for k in args.param_exp_override)

    optional_params = paramsOverride + paramsExportOverride

    parameters = __load_cloudformation_config(env_conf_file=args.config_file, optinal_params=optional_params, config=config)

    stack_info = {
        'stack_name': args.stack_name,
        'template_file': args.template_file,
        'parameters': parameters,
        'capabilities': args.capabilities if args.capabilities and len(args.capabilities) > 0 else [],
        'region': args.region
    }

    cf_client = session.current.client('cloudformation')

    try:
        __deploy_stack(stack_info=stack_info, cf_client=cf_client)
    except Exception as e:
        print("Failed create a stack {}".format(e.message))
        response = cf_client.describe_stack_events(
            StackName=stack_info['stack_name']
        )
        print("Stack related events in reverse chronological order {}".format(
            prettify(response)))
        exit(1)

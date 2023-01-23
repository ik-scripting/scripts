#!/usr/bin/env python
'''
  Create/Update Elastic Container Service environment.
  Support deploy different version of application and configuration.


  Usage example:
    export AWS_DEFAULT_REGION=eu-west-1

  ./ecs_create_service.py \
  --ecsTaskDef "../tests/ecs/sample-ecs-task-def.conf.json" \
  --targetGroupConfFile "../tests/ecs/sample-targetgroup.conf.json" \
  --listenerRuleConfFile "../tests/ecs/sample-listenerrule.conf.json" \
  --serviceConfFile "../tests/ecs/sample-service.conf.json" \
  --localDeployConfFile "../tests/deploy-env/sample.conf.json" \
  --remoteDeployConfFile "../tests/deploy-env/cluster.conf.json" \
  --buildParams Image=httpd \
  ProjectName=sample-service \
  ClusterName=enterprise-services-ecs-cluster \
  Version=1.0.1 \
  Env=dev

'''

import argparse

parser = argparse.ArgumentParser(description='Process Arguments.')
parser.add_argument('--ecsTaskDef', type=str, required=True, dest='ecs_task_def_file')
parser.add_argument('--targetGroupConfFile', type=str, required=True, dest='target_group_conf_file')
parser.add_argument('--listenerRuleConfFile', type=str, required=True, dest='listener_rule_conf_file')
parser.add_argument('--serviceConfFile', type=str, required=True, dest='service_conf_file')
parser.add_argument('--localDeployConfFile', type=str, required=True, dest='local_deploy_config_file')
parser.add_argument('--remoteDeployConfFile', type=str, required=True, dest='remote_deploy_config_file')
parser.add_argument('--buildParams', type=str, required=True, nargs='*', dest='build_params',
                    help='Build parameters. Usage: e.g. \"Key1=Value\" \"Key2=Value\".')

MAJOR_VERSION_INDEX = 0

if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from py.core.session import Session
    from py.core.config import Config
    from py.core.exports import Exports
    from py.elbv2.load_balancer import create_update_targetgroup, create_update_listener_rule
    from py.ecs.service import create_update_service
    from py.ecs.config import ClusterConfig
    from py.core.utils import read_template, prettify

    from py.ecs.task_def import register_task_def
    from py.ecs.waiter import waiter
    from py.cloudwatch.logs import create_update_log_group


    args = parser.parse_args()
    session = Session.factory()
    exports = Exports(session)
    config = Config(exports)
    ecs_config = ClusterConfig(exports)

    build_params = config.convert_key_value_input_to_dict(args.build_params)

    version = "v{}".format(build_params['Version'].split('.')[MAJOR_VERSION_INDEX])
    service_name = "{}-{}-{}".format(build_params['ProjectName'], version, build_params['Env'])

    # merge all configuration into one set
    remote_deploy_config = ecs_config.read_remote_cluster_config(config=read_template(args.remote_deploy_config_file), 
                                                      key_name=build_params['ClusterName'])

    local_deploy_config = config.load_environment_dict(env_conf_file=args.local_deploy_config_file)

    final_config = config.merge_dictionaries(remote_deploy_config, local_deploy_config, build_params)

    final_config['Version'] = version
    final_config['ServiceName'] = service_name

    print("=============================")
    print "Read config {}".format(prettify(final_config))
    print("=============================")

    create_update_log_group(group_name=final_config['ServiceName'], session=session)

    template_config = config.load_resource_config(args.ecs_task_def_file, final_config)
    taskArn = register_task_def(template=template_config, session=session)

    template_config = config.load_resource_config(args.target_group_conf_file, final_config)
    final_config['TargetGroupArn'] = create_update_targetgroup(load_balancer_arn=final_config['LoadBalancer'],
                                                                template_config=template_config,
                                                                session=session)

    template_config = config.load_resource_config(args.listener_rule_conf_file, final_config)
    create_update_listener_rule(template_config, session)

    template_config = config.load_resource_config(args.service_conf_file, final_config)
    desiredCount = int(template_config['desiredCount'])
    create_update_service(template_config, session)

    # a watcher to confirm successful deployment

    waiter(session=session,
           cluster=final_config['ClusterArn'], service=final_config['ServiceName'],
           task=taskArn, target_group=final_config['TargetGroupArn'],
           desired_count=desiredCount)

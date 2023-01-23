#!/usr/bin/env python
"""
 Creates / updates a Cloudwatch dashboard
"""
import argparse
import botocore


def parse_args():
    parser = argparse.ArgumentParser(description='Create or update Cloudwatch dashboard for elastic beanstalk application.')
    parser.add_argument('--file', required=True, help='Dashboard template JSON file')
    parser.add_argument('--name', required=True, help='Application name for dashboard')
    parser.add_argument('--appEnvironment', type=str, required=True, dest='app_environment')
    parser.add_argument('--env', required=True, help='Name fragment indicating the environment, e.g. dev, preprod, prod')
    parser.add_argument('--region', type=str, required=True, dest='region')
    return parser.parse_args()


if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from py.core.session import Session

    args = parse_args()

    session = Session.factory(region=args.region)

    dashboard_name = args.name + '-' + args.env + '-dashboard'

    eb_client = session.current.client('elasticbeanstalk')

    # load beanstalk resources
    response = eb_client.describe_environment_resources(
        EnvironmentName=args.app_environment
    )

    asg_name = response['EnvironmentResources']["AutoScalingGroups"][0]["Name"]
    elb_name = response['EnvironmentResources']["LoadBalancers"][0]["Name"]

    short_elb_name = elb_name.split(":loadbalancer/")[-1]

    eb_client = session.current.client('elasticbeanstalk')

    elbv2_client = session.current.client('elbv2')

    response = elbv2_client.describe_target_groups(
        LoadBalancerArn=elb_name
    )

    # OK to hardcode for one target group for now
    elb_target_name = response['TargetGroups'][0]['TargetGroupArn'].split(":")[-1]

    with open(args.file, 'r') as dashboard_json_file:
        raw_dashboard_json = dashboard_json_file.read()

    dashboard_json = raw_dashboard_json.replace("__ENVIRONMENT_NAME__", args.env)
    dashboard_json = dashboard_json.replace("__ASG_NAME__", asg_name)
    dashboard_json = dashboard_json.replace("__APP_ELB_NAME__", short_elb_name)
    dashboard_json = dashboard_json.replace("__TARGET_GROUP_NAME__", elb_target_name)

    cloudwatch = session.current.client('cloudwatch')

    try:
        response = cloudwatch.put_dashboard(
            DashboardName=dashboard_name,
            DashboardBody=dashboard_json
        )
        print response
    except botocore.exceptions.ClientError as ex:
        print "Aborting: {}".format(ex)
        raise ex

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Usage
# ./main.py --attach
# ./main.py --detach

import logging, argparse
import boto3

import src.utils as utils
import src.models.asg as asg
import src.models.ec2 as ec2

default_log_args = {
    "level": logging.INFO,
    "format": "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}

logging.basicConfig(**default_log_args)
log = logging.getLogger("asg-sg")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI to manage ASG nodes. Every command represent 'commands' block in 'config.yaml'")

    parser.add_argument('--attach', action='store_true', help="Attach Security Group")
    parser.add_argument('--detach', action='store_true', help="Detach Security Group")
    args = parser.parse_args()

    args_data = utils.read_from_yml_file("config.yaml")

    client_asg = boto3.client('autoscaling')
    client_ec2 = boto3.client('ec2')

    asg_result = asg.ASG(client=client_asg, name=args_data['asg_name'], logging=logging)
    logging.info(f'asg: \"{args_data["asg_name"]}\"')
    logging.info(f'instances: "{asg_result._instance_ids}"')
    action = 'attach' if args.attach else 'detach'
    ec2_result = ec2.EC2Instances(client=client_ec2, ids=asg_result._instance_ids, sg_id=args_data['sg'], action=action, logging=logging)
    logging.info(ec2_result)

    if args.attach:
        ec2_result.attach()
    elif args.detach:
        ec2_result.detach()


#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Usage
# ./main.py --read-config --taints
# ./main.py --migrate-asg

# read kubectl
# boto3 access to autoscaling group
# update cluster autoscaler tag e.g. disable
# pick 2 nodes to cordone,drain and terminate
# choose X nodes to cordone,draing and terminate
import os, logging, time
import argparse
import boto3

import utils

import models.asg as asg
import models.ec2 as ec2
import models.ks8client as k8s
from models.cm import CMDs
from models.slack import Slack


default_log_args = {
    "level": logging.INFO,
    "format": "%(asctime)s [%(levelname)s] - %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}

first_asg = 0
time_in_seconds_to_avoid_request_failures = 40

logging.basicConfig(**default_log_args)
log = logging.getLogger("eks-drain-nodes")

def migrate_asg(**kwargs: object) -> None:
    """
    - Read all EC2 in ASG
    - Describe all nodes in ASG
    - Identify nodes to Taint/Untaint
    """
    cmds = kwargs.get('cmds')
    migrate = cmds.migrate_asg
    k8s_client = kwargs.get('k8s_client')
    asg_client = kwargs.get('asg_client')
    ec2_client = kwargs.get('ec2_client')
    slack = kwargs.get('slack')

    asg_name = migrate.asg_name
    num_instances = migrate.scaledown_increment
    isnth = migrate.nth

    asg_result = asg.ASG(client=asg_client,name=asg_name, num_instances=num_instances, logging=logging)
    logging.debug(utils.json_prettify(asg_result._asg))
    if asg_result.autoscaler:
        asg_result.disable_autoscaler()
    else:
        logging.info("❎ cluster autoscaler disabled")

    if asg_result.instanceProtection:
        asg_result.disable_instanceProtection()
    else:
        logging.info("❎ protect_from_scale_in is set to false")

    ids = asg_result._instance_ids_to_drain
    if len(ids) == 0:
        logging.info("❎ no instances found to Cordon, Drain and Terminate")
        os._exit(0)

    # os._exit(1)
    msg = "scale down nodes for ASG"
    slack.post_message_to_slack(msg=f"🤠 START: {msg}. Account:{cmds.account}. ASG:'{asg_name}'.", ctx=f"batch of {num_instances} instance(s).")

    k8s_client = k8s.K8sClient(logger=logging, grace_period=time_in_seconds_to_avoid_request_failures)

    ec2_result = ec2.EC2Instances(client=ec2_client, ids=ids, logging=logging)
    logging.info(ec2_result._instances)
    count = 0
    for el in ec2_result._instances:
        logging.info(f'Start: Taint, Cordon and Drain node {el}')
        k8s_client.patch_worker(name=el.name, isnth=isnth)
        logging.info(f'🔰 Start: Terminate {el}')
        time.sleep(time_in_seconds_to_avoid_request_failures)
        asg_result.terminate_instance(el.id)
        count += 1
        logging.info(f"⚠️  Terminated '{count}' instances. Left to process {len(ec2_result._instances) - count}...")

    slack.post_message_to_slack(msg=f"🥳 SUCCESS: {msg}. Account:{cmds.account}. ASG:'{asg_name}'.", ctx=f"current ASG size {asg_result.asg_size_after}(-{num_instances}) instance(s). Attach DD screenshot with Unavailable Pods and Misscheduled DaemonSets...")

def taint_nodes_in_asg(**kwargs: object) -> None:
    """
    - Read all EC2 in ASG
    - Describe all nodes in ASG
    - Identify nodes to Taint/Untaint
    """
    cmds = kwargs.get('cmds')
    taints = cmds.taints
    k8s_client = kwargs.get('k8s_client')
    slack = kwargs.get('slack')
    msg = "taint all nodes for ASG" if taints.taint_asg else "untaint all nodes for ASG"
    # slack.post_message_to_slack(msg=f"👁️ START: {msg}. Selector:'{taints.label_selector}'. Account:{cmds.account}")

    if taints.taint_asg:
        k8s_client.taint_nodes(label_selector=taints.label_selector)
    elif taints.untaint_asg:
        k8s_client.untaint_nodes(label_selector=taints.label_selector)

    # if taints.legacy:
    #     asg_client = kwargs.get('asg_client')
    #     ec2_client = kwargs.get('ec2_client')
    #     asg_result = asg.ASG(client=asg_client,name=taints.asg_name, num_instances=float('inf'), logging=logging)
    #     ec2_taint = ec2.EC2Instances(client=ec2_client, ids=asg_result._instance_ids, logging=logging)
    #     if taints.taint_asg:
    #         k8s_client.taint_nodes(node_names=ec2_taint._instances_names)
    #     elif taints.untaint_asg:
    #         k8s_client.untaint_nodes(node_names=ec2_taint._instances_names)

    if taints.taint_asg:
        logging.info(f'❎ Success: taints all required nodes. Legacy:{taints.legacy}')
    elif taints.untaint_asg:
        logging.info(f'❎ Success: untaints all required nodes. Legacy:{taints.legacy}')

    # slack.post_message_to_slack(msg=f"❎ SUCCESS: {msg}. Selector:'{taints.label_selector}'. Account:{cmds.account}")

def recycle(**kwargs: object) -> None:
    """
    """
    cmds = kwargs.get('cmds')
    cmd = cmds.recycle
    k8s_client = kwargs.get('k8s_client')
    k8s_client.recycle_nodes(label_selector=cmd.label_selector)

def test_slack(**kwargs: object) -> None:
    """
    - Read slack SSM secret
    - Send test message
    """
    slack = kwargs.get('slack')
    slack.post_message_to_slack(msg="START: node group migration. TEST", ctx="scale down increment 4. to scale down 65.TEST")

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="CLI to manage EKS nodes, patching and upgrades. Every command represent 'commands' block in 'config.yaml'")

  parser.add_argument('--taints', action=argparse.BooleanOptionalAction, help = "Add|Remove taint from all nodes in ASG")
  parser.add_argument('--migrate-asg', action='store_true', help = "Cordone and Scale Down ASG")
  parser.add_argument('--recycle', action='store_true', help = "Recycle node group in place")
  parser.add_argument('--test-slack', action='store_true', help="Test slack notification")
  parser.add_argument('--read-config', action='store_true', help="Read config file")

  args = parser.parse_args()

  args_data = utils.read_from_yml_file("config.yaml")

  if args.read_config:
    print(utils.yaml_prettify(args_data))

  result = boto3.client('sts').get_caller_identity()

  args_data["account_id"] = result["Account"]
  cmds = CMDs.factory(args_data)

  logging.info(f"{cmds}")

  result = boto3.client('sts').get_caller_identity()

  kwargs = {
    'asg_client': boto3.client('autoscaling'),
    'ec2_client': boto3.client('ec2'),
    'slack': Slack(ssm_token_id=cmds.slack.ssm_token_id, ssm_client=boto3.client('ssm'),
    channel=cmds.slack.channel, username=cmds.slack.name),
    'k8s_client': k8s.K8sClient(logger=logging, grace_period=time_in_seconds_to_avoid_request_failures),
    'cmds': cmds
  }

  if args.taints:
    taint_nodes_in_asg(**kwargs)
  elif args.migrate_asg:
    migrate_asg(**kwargs)
  elif args.recycle:
    recycle(**kwargs)
  elif args.test_slack:
    test_slack(**kwargs)

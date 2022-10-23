# -*- coding: utf-8 -*-


import logging

class ASG:

    def __init__(self, client, name, num_instances, logging=None):
        """

        @param client:
        @param logging:
        """
        self.client = client
        self.logging = logging
        self.name = name
        self.num_instances = num_instances
        self._asg = self.get_asg(name)
        self._min_size = self._asg['MinSize']
        self._max_size = self._asg['MaxSize']
        self._res_id = name
        self._res_type = "auto-scaling-group"
        self._tags = self._asg['Tags']
        self._flatten_tags = self.get_flatten_tags(self._asg)
        self._instance_ids = self.get_flatten_ids(float('inf'), self._asg)
        self.logging.info(f"fetch instances: {len(self._instance_ids)}")
        self._instance_ids_to_drain = self.get_flatten_ids(num_instances, self._asg)
        self.asg_size_after = len(self._instance_ids) - len(self._instance_ids_to_drain)
        self.logging.debug(f"ASG {len(self._instance_ids)}. Scaling down to {self.asg_size_after}")
        self.scale_down_asg = self._min_size <= self.asg_size_after


    def get_asg(self, name):
      response = self.client.describe_auto_scaling_groups(
        AutoScalingGroupNames=[
            name,
        ],
        MaxRecords=100,
      )
      if len(response["AutoScalingGroups"]) == 0:
        msg = f"autoscaling group '{name}' not found"
        self.logging.error(msg)
        raise ValueError(msg)
      if len(response["AutoScalingGroups"]) > 1:
        msg = f"must be only single ASG found"
        self.logging.error(msg)
        raise ValueError(msg)
      return response["AutoScalingGroups"][0]

    def get_flatten_tags(self, asg):
      tags = asg["Tags"]
      result = {}
      for tag in tags:
        result[tag["Key"]] =  tag["Value"]
      return result

    def get_flatten_ids(self, num, asg):
      elements = asg["Instances"]
      result = []
      for el in elements:
        if el['LifecycleState'] == 'InService' and el['HealthStatus'] == 'Healthy' and len(result) < num:
          result.append(el['InstanceId'])
        elif len(result) < num:
          continue
        else:
            break
      return result

    @property
    def autoscaler(self):
      enabled = 'k8s.io/cluster-autoscaler/enabled'
      disabled = 'k8s.io/cluster-autoscaler/disabled'
      if enabled in self._flatten_tags:
        self.logging.info(f"Tag '{enabled}' found. Updating....")
        return True
      if disabled in self._flatten_tags:
        self.logging.info(f"Tag '{disabled}' found. Skipping....")
        return False
      msg = f"Tag '{enabled}' or '{disabled}' not FOUND"
      self.logging.error(msg)
      raise ValueError(msg)

    @property
    def instanceProtection(self):
      return self._asg['NewInstancesProtectedFromScaleIn']

    def disable_autoscaler(self):
      delete_tag = 'k8s.io/cluster-autoscaler/enabled'
      update_tag = 'k8s.io/cluster-autoscaler/disabled'
      self.logging.info(f"update tag '{delete_tag}' with '{update_tag}'")
      try:
        response = self.client.delete_tags(
            Tags=[
                {
                    'ResourceId': self._res_id,
                    'ResourceType': self._res_type,
                    'Key': delete_tag,
                    'Value': 'true',
                },
            ]
        )
        if 'HTTPStatusCode' in response['ResponseMetadata'] and response['ResponseMetadata']['HTTPStatusCode'] == 200:
          logging.info(f"Deleted tag {delete_tag}")
        else:
          raise Exception(f'exception when deleting a tag {delete_tag}')
        response = self.client.create_or_update_tags(
            Tags=[
                {
                    'ResourceId': self._res_id,
                    'ResourceType': self._res_type,
                    'Key': update_tag,
                    'Value': 'true',
                    'PropagateAtLaunch': False
                },
            ]
        )
        if 'HTTPStatusCode' in response['ResponseMetadata'] and response['ResponseMetadata']['HTTPStatusCode'] == 200:
          logging.info(f"Update tag {update_tag}")
        else:
          raise Exception(f'exception when creating a new tag {update_tag}')
      except Exception as e:
        raise ValueError(e)

    def disable_instanceProtection(self):
      logging.info("Disable Instance Protection From Scale In")
      try:
        response = self.client.update_auto_scaling_group(
            AutoScalingGroupName=self.name,
            NewInstancesProtectedFromScaleIn=False,
        )
        if 'HTTPStatusCode' in response['ResponseMetadata'] and response['ResponseMetadata']['HTTPStatusCode'] == 200:
          logging.info('disable "NewInstancesProtectedFromScaleIn"')
        else:
          raise Exception(f'exception when disabling "NewInstancesProtectedFromScaleIn"')
      except Exception as e:
        raise ValueError(e)

    def terminate_instance(self, id):
      logging.info("Terminate instance in autoscaling group")
      if not self.scale_down_asg:
        logging.info("ShouldDecrementDesiredCapacity set to False. The min ASG capacity should be decreased.")
      try:
        response = self.client.terminate_instance_in_auto_scaling_group(
            InstanceId=id,
            ShouldDecrementDesiredCapacity=self.scale_down_asg
        )
        if 'HTTPStatusCode' in response['ResponseMetadata'] and response['ResponseMetadata']['HTTPStatusCode'] == 200:
          pass
        else:
          raise Exception(f'exception when terminating instance "{id}"')
      except Exception as e:
        self.logging.error(f"not able to terminate instance '{id}' .exception: {e}. Processing next instance")

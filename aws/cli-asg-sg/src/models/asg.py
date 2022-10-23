# -*- coding: utf-8 -*-



class ASG:

    def __init__(self, client, name, logging=None):
        """
        @param client:
        @param logging:
        """
        self.client = client
        self.logging = logging
        self.name = name
        self._asg = self.get_asg(name)
        self._res_id = name
        self._instance_ids = self.get_flatten_ids(float('inf'), self._asg)
        self.logging.info(f"fetch instances: {len(self._instance_ids)}")
        self.logging.debug(f"ASG {len(self._instance_ids)}.")


    def get_asg(self, name):
      """
      TODO: only 100 instances supported. Should be fixed
      """
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

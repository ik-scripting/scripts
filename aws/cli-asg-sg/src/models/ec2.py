# -*- coding: utf-8 -*-

import json, boto3
from operator import mod
import logging

class EC2Instances:

    def __init__(self, client, ids, sg_id, action, logging=None):
        """
        @param client:
        @param cluster:
        @param role:
        """
        self.client = client
        self.ec2 = boto3.resource('ec2')
        self.sg_id = sg_id
        self.log = logging
        self.action = action
        # self.security_group = client.SecurityGroup('id')
        # self.sg = self.fetch_security_group(sg_id)
        self._instances = self.fetch_instances(ids)
        self.process = len(self._instances) > 0

    def fetch_security_group(self, id):
        try:
            response = self.client.describe_security_groups(GroupIds=[id])
            if response['ResponseMetadata'] and response['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise Exception(f'not 200')
            security_group = response['SecurityGroups'][0]
            self.log.debug(json.dumps(response['SecurityGroups'], indent=4, default=str))
            return {
                "GroupName": security_group['GroupName'],
                "GroupId": security_group['GroupId']
                }
        except Exception:
            raise Exception(f'exception when trying to fetch security group data "{id}"')

    def fetch_instances(self, ids):
        """
        Describes the specified instances for desired role.

        @param cluster: cluster name
        @param role: instance role e.g. master|node|etcd
        @param desired_instance_age: desired age
        @return: collection of instances
        """
        result = []
        self.log.debug(f"fetch '{len(ids)}' instances")
        self.log.debug(f"fetch instance data for ids '{ids}'")
        try:
          response = self.client.describe_instances(
              InstanceIds=ids
          )
          if 'HTTPStatusCode' in response['ResponseMetadata'] and response['ResponseMetadata']['HTTPStatusCode'] == 200:
            pass
          else:
            raise Exception(f'not able to fetch instacnes with ids: {ids}')
          if len(response['Reservations'][0]['Instances']) == 0:
            raise Exception(f'should retrun at least single insatance data')
          result = []
          for reservation in response["Reservations"]:
              for el in reservation["Instances"]:
                ec2 = EC2Instance.factory(el)
                if ec2.state and self.action == 'attach' and self.sg_id not in ec2.groups:
                    result.append(ec2)
                elif ec2.state and self.action == 'detach' and self.sg_id in ec2.groups:
                    result.append(ec2)
                else:
                  self.log.warn(f'instance "{ec2.id}" excluded')
        except:
          raise Exception(f'exception when trying to fetch instance data {ids}')
        return result

    def attach(self):
        if not self.process:
            self.log.info('nothing to attach')
            return
        self.log.info('attach')
        for el in self._instances:
            instance = self.ec2.Instance(el.id)
            ec2 = EC2Resource.factory(instance)
            ec2.attach(self.sg_id)


    def detach(self):
        if not self.process:
            self.log.info('nothing to detach')
            return
        self.log.info('detach')
        for el in self._instances:
            instance = self.ec2.Instance(el.id)
            ec2 = EC2Resource.factory(instance)
            ec2.detach(self.sg_id)

    def __str__(self):
        return f'total: {len(self._instances)}, instances: {self._instances}'

    def __repr__(self):
        return self.__str__()

class EC2Resource:

    def __init__(self, input) -> None:
        self.id = input.id
        self.security_groups = input.security_groups
        # move out, as it could be done once for 'attach|detach'
        self.security_group_ids = [sg['GroupId'] for sg in input.security_groups]
        self.network_interfaces = input.network_interfaces
        self.instance = input
        self.type = input.instance_type
        self.log = logging.getLogger("ec2-resource")

    def attach(self, sg):
        """
        Changes the security group of an instance. Security groups are associated with
        the instance's network interfaces, so this function iterates the list of
        network interfaces associated with the specified instance and updates each
        network interface by replacing the old security group with the new security group.

        :param sg: The ID of the security group.
        """
        self.log.info(f'attach to instance "{self.id}" and sg is "{sg}"')
        before = len(self.security_groups)
        modified = [sg]
        for el in self.security_group_ids:
            modified.append(el)
        try:
            # There are multiple interfaces attached to instance 'ec2'. Please specify an interface ID for the operation instead.
            for network_interface in self.network_interfaces:
                network_interface.modify_attribute(
                    Groups = modified
                )
        except Exception:
            msg = f"Couldn't update network interfaces for instance \"{self.id}\"s."
            self.log.exception(msg)
            raise
        self.log.info(f"before: {before}, after: {len(modified)}")

    def detach(self, sg):
        """
        Changes the security group of an instance. Security groups are associated with
        the instance's network interfaces, so this function iterates the list of
        network interfaces associated with the specified instance and updates each
        network interface by replacing the old security group with the new security group.

        :param sg: The ID of the security group.
        """
        self.log.info(f'detach from instance "{self.id}" and sg is "{sg}"')
        before = len(self.security_groups)
        modified = []
        for el in self.security_group_ids:
            if sg != el:
                modified.append(el)
        try:
            for network_interface in self.network_interfaces:
                network_interface.modify_attribute(
                    Groups = modified
                )
        except Exception:
            msg = f"Couldn't update network interfaces for instance \"{self.id}\"s."
            self.log.exception(msg)
            raise
        self.log.info(f"before: {before}, after: {len(modified)}")

    @staticmethod
    def factory(dct):
        return EC2Resource(dct)

    def __str__(self):
        return f'id: {self.id}, sg: {self.sg}'

    def __repr__(self):
        return self.__str__()

class EC2Instance:

    def __init__(self, input):
        self.id = input['InstanceId']
        self.ip = input['PrivateIpAddress']
        self.name = input['PrivateDnsName']
        self.dns = input['PrivateDnsName']
        self.sgs = input['SecurityGroups']
        # print(json.dumps(input, indent=4, default=str))
        self.groups = self._groups()
        self.state = True if input['State']['Name'] == 'running' else False
        self.stateName = input['State']['Name'] == 'running'

    def _groups(self):
        return [x['GroupId'] for x in self.sgs]

    @staticmethod
    def factory(dct):
        return EC2Instance(dct)

    def __str__(self):
        return f'[id:{self.id}]'

    def __repr__(self):
        return self.__str__()

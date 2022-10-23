# -*- coding: utf-8 -*-


import datetime

class EC2Instances:

    def __init__(self, client, ids, logging=None):
        """
        @param client:
        @param cluster:
        @param role:
        """
        self.client = client
        self.log = logging
        self._instances = self.fetch_instances(ids)
        self._instances_names = [x.name for x in self._instances]

    def fetch_instances(self, ids):
        """
        Describes the specified instances for desired role.

        @param cluster: cluster name
        @param role: instance role e.g. master|node|etcd
        @param desired_instance_age: desired age
        @return: collection of instances
        """
        result = []
        self.log.info(f"fetch '{len(ids)}' instances")
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
                if ec2.state:
                  result.append(ec2)
                else:
                  self.log.warn(f'instance "{ec2.id}" excluded')
        except Exception as e:
          raise Exception(f'exception when trying to fetch instance data {ids}')
        return sorted(list(result), key=lambda instance: instance.launch_time)

    def __str__(self):
        return f'total: {len(self._instances)}, instances: {self._instances}'

    def __repr__(self):
        return self.__str__()


class EC2Instance:

    def __init__(self, input):
        self.id = input['InstanceId']
        self.ip = input['PrivateIpAddress']
        self.name = input['PrivateDnsName']
        self.dns = input['PrivateDnsName']
        self.ami = input['ImageId']
        self.state = True if input['State']['Name'] == 'running' else False
        self.stateName = input['State']['Name'] == 'running'
        self.launch_time = input['LaunchTime'].date()
        self.age = (datetime.date.today() - self.launch_time).days

    def is_ready_for_patching(self):
        return self.age >= self.desired_instance_age

    @staticmethod
    def factory(dct):
        return EC2Instance(dct)

    def __str__(self):
        return f'[id:{self.id}, age:{self.age}d, name:{self.dns}]'

    def __repr__(self):
        return self.__str__()

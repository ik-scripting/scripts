#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# DSL to help identify services that are using privileged ports.
# Story: https://hbidigital.atlassian.net/browse/PAAS-1439

# Prerequisits
# pip install pyaml
# kubernetes is accessble
# kubectl is installed

# bin/privileged-ports.py --ns apps

# Read configuration from local files
# kubectl get configmap -o yaml > configmaps.yaml
# kubectl get deploy -o yaml > deploy.yaml
# bin/privileged-ports.py --ns apps --local-file

from datetime import datetime
import subprocess
import logging, argparse

from utils import utils

default_log_args = {
    "level": logging.INFO,
    "format": "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}
logging.basicConfig(**default_log_args)
log = logging.getLogger("ports")

PRIVILEGED_PORT_MAX=1024
LIST_ALL_DEPLOYMENTS="kubectl get deploy -o yaml --namespace {namespace}"
LIST_ALL_CONFIGMAPS="kubectl get configmap -o yaml --namespace {namespace}"

def read_deployments(namespace):
    process = subprocess.run(LIST_ALL_DEPLOYMENTS.format(namespace = namespace).split(), stdout=subprocess.PIPE)
    output = process.stdout.decode('utf-8')
    return utils.read_from_yml(output)

def read_configmaps(namespace):
    process = subprocess.run(LIST_ALL_CONFIGMAPS.format(namespace = namespace).split(), stdout=subprocess.PIPE)
    output = process.stdout.decode('utf-8')
    return utils.read_from_yml(output)

# models

class Configmaps:

    def __init__(self, data):
        self.data = data
        self.elements = self.configmaps()
        self.length = len(self.elements)

    @staticmethod
    def factory(data):
        return Configmaps(data)

    def configmaps(self):
        """
        only process configmaps with '-metadata' suffix
        """
        result = {}
        for el in self.data['items']:
            try:
                if '-metadata' in el['metadata']['name'] and 'service_type' in el['data'] and 'deployment' in el['data']['service_type']:
                    cfg = Configmap(el)
                    result[cfg.name] = cfg
            except:
                print(f'Not able to process {el}')
                raise AttributeError
        return result

    def __str__(self):
        return f'Configmaps {self.length}'

class Configmap:

    def __init__(self, source):
        self.data = source
        self.fullname = source['metadata']['name']
        self.name = self.fullname.replace("-metadata", "")
        data = source['data']
        self.repository = data['repository']
        self.team = data['team']
        self.k8s_deploy = data['k8s_deploy_version']
        self.deployment_date = data['deployment_date']
        self.age = (datetime.utcnow() - datetime.strptime(self.deployment_date, '%Y-%m-%d')).days

    def __str__(self):
        return f'Configmap: {self.name}. Repository: {self.repository}. Team: {self.team}. K8s-Deploy: {self.k8s_deploy}. Deployment Date: {self.deployment_date}. Age: {self.age} days'

class Deployments:

    def __init__(self, data):
        self.data = data
        self.full_length = 0
        self.elements = self.deployments()
        self.length = len(self.elements)

    @staticmethod
    def factory(data):
        return Deployments(data)

    def deployments(self):
        result = []
        for el in self.data['items']:
            self.full_length += 1
            deployment = Deployment(el)
            if deployment.is_privileged:
                result.append(deployment)
        return result

    def __str__(self):
        return f'Deployments {self.length}'


class Deployment:

    def __init__(self, data):
        self.data = data
        self.fullname = data['metadata']['name']
        self.name = self.fullname.replace("-helm", "")
        self.ports = self.extract_ports()
        self.container = self.data['spec']['template']['spec']['containers'][0]['image']
        self.is_privileged = self.is_privileged_ports()
        self.team = data['metadata']['labels']['team'] if 'team' in data['metadata']['labels'] else 'None'
        self.creationdate = data['metadata']['creationTimestamp']
        self.age = (datetime.utcnow() - datetime.strptime(self.creationdate, '%Y-%m-%dT%H:%M:%SZ')).days

    def extract_ports(self):
        result = set()
        for el in self.data['spec']['template']['spec']['containers']:
            try:
                for port in el['ports']:
                    result.add(port['containerPort'])
            except:
                print(f"No ports configured for HELM deployment: {self.data['metadata']['name']}")
        return list(result)

    def is_privileged_ports(self):
        for port in self.ports:
            if PRIVILEGED_PORT_MAX >= port:
                return True
        return False

    @staticmethod
    def factory(data):
        return Deployment(data)

    def __str__(self):
        ports = ','.join(str(e) for e in self.ports)
        return f'Deployment: {self.name}. Team: {self.team}. Ports: "{ports}"'

class Result:

    def __init__(self, deployments, configmaps, namespace):
        self.deployments = deployments
        self.configmaps = configmaps
        self.namespace = namespace

    def group_by_team(self):
        """
        group deployments by team
        """
        result = {}
        for el in self.deployments.elements:
            team = el.team.lower()
            if team in result:
                elements = result[team]
                elements.append(el)
                result[team] = elements
            else:
                result[team] = [el]
        return result

    def process(self):
        for team, elements in self.group_by_team().items():
            print(f'\n+++++ TEAM "{team}". Number of services {len(elements)} +++++\n')
            for el in elements:
                name = el.name
                print(f'Non-compliant service "{name}"')
                print(f'\tTeam: {el.team}')
                if name in self.configmaps.elements:
                    cfg = self.configmaps.elements[name]
                    print(f'\tRepository is "{cfg.repository}"')
                    print(f'\tVersion k8s-deploy is "{cfg.k8s_deploy}"')
                    print(f'\tDeployment age "{cfg.age}" days')
                else:
                    print(f'\tContainer: {el.container}')
                    print(f'\tDeployment age {el.age} days')

                print(f'\tContainerPorts: {el.ports}')

    def output(self):
        for el in self.configmaps.elements:
            print(el)
        for el in self.deployments.elements:
            print(el)

    def __str__(self):
        return f"Processed {self.deployments.full_length} deployments in namespace '{self.namespace}'. Found {self.deployments.length} non-compliant."

class Entity:

    def __init__(self, svc_name, team, ports, repository, cfg_age, deploy_age, container):
        self.name = svc_name
        self.team = team
        self.repository = repository
        self.cfg_age = cfg_age
        self.deploy_age = deploy_age
        self.container = container
        self.ports = ports

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="CLI to identify services that uses privileged ports.")
    parser.add_argument('--ns', help = "Namespace scope for this request.")
    parser.add_argument('--local-file', action='store_true', help = "Read from local files. When not present, kubectl is used.")

    args = parser.parse_args()
    namespace = args.ns

    data_cfg = utils.read_from_yml_file("configmaps.yaml") if args.local_file else read_configmaps(namespace)
    data_deploy = utils.read_from_yml_file("deploy.yaml") if args.local_file else read_deployments(namespace)

    cfgs = Configmaps(data_cfg)
    deploy = Deployments(data_deploy)
    result = Result(deployments=deploy, configmaps=cfgs, namespace=args.ns)

    result.process()
    print(result)

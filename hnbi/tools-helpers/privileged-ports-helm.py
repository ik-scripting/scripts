#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# DSL to help identify services that are using privileged ports.
# !!!Helm solution is extremely slow!!!

# Prerequisits
# pip install pyaml
# kubernetes is accessble

# bin/privileged-ports.py --ns apps-customer
# Namespaces
# apps-spange
# apps-sellerx
# apps-paas
# apps-customer V
# apps-composer
# apps-attract
# apps

import subprocess
import logging, argparse
import yaml

default_log_args = {
    "level": logging.INFO,
    "format": "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    "datefmt": "%d-%b-%y %H:%M",
    "force": True,
}
logging.basicConfig(**default_log_args)
log = logging.getLogger("ports")

LIST_ALL_HELM_CHARTS_IN_NAMESPACE="helm ls --all --short --namespace {namespace} --max 10000"
GET_HELM_CHART_VALUES="helm get values {name} -o yaml --namespace {namespace}"
GET_CONFIGMAP="kubectl get Configmap {name} -o yaml --namespace {namespace}"
PRIVILEGED_PORT_MAX=1024

def read_from_yml(input):
    return yaml.safe_load(input)

def extract_values(chart_name, namespace):
    process = subprocess.run(GET_HELM_CHART_VALUES.format(name = chart_name, namespace = namespace).split(), stdout=subprocess.PIPE)
    output=process.stdout.decode('utf-8')
    ports = []
    result = []
    try:
        ports = read_from_yml(output)['ports']
        for el in ports:
            port = el['containerPort']
            if PRIVILEGED_PORT_MAX >= port:
                result.append(el['containerPort'])
    except Exception as e:
        print(f"Exception occurred for helm chart '{chart_name}': {repr(e)}")
    return result

def extract_details_from_configmap(name, namespace):
    process = subprocess.run(GET_CONFIGMAP.format(name = name, namespace = namespace).split(), stdout=subprocess.PIPE)
    try:
        output = process.stdout.decode('utf-8')
        data = read_from_yml(output)['data']
        return f"team: {data['team']}. repository: {data['repository']}. deployment_date: {data['deployment_date']}"
    except Exception as e:
        # print(f"Exception occurred for helm chart '{name}': {repr(e)}")
        return "--No MetaData Found--"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="CLI to identify services that uses privileged ports.")
    parser.add_argument('--ns', help = "Namespace scope for this request")

    args = parser.parse_args()

    result = subprocess.run(LIST_ALL_HELM_CHARTS_IN_NAMESPACE.format(namespace = args.ns).split(), stdout=subprocess.PIPE)
    output=result.stdout.decode('utf-8').split("\n")[:-1]
    count = 0
    for el in output:
        if 'cron' in el:
            continue
        ports = extract_values(el, args.ns)
        if len(ports) > 0:
            count += 1
            configmap_name = el.replace("-helm", "-metadata")
            info = extract_details_from_configmap(configmap_name, args.ns)
            print(f'helm chart: {el}. ports: {ports}. metadata >> {info}')

    log.info(f"For namespace '{args.ns}' found '{count}' services that has to be migrated out of {len(output)}.")




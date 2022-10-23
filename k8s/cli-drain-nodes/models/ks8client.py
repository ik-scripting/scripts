# -*- coding: utf-8 -*-

from datetime import datetime, timezone
from kubernetes import client as k8s_client, config
import subprocess


from .kubectl import Kubectl

node_cordon_body = {
    "spec": {
        "unschedulable": True
    }
}

class K8sClient:

    def __init__(self, logger, grace_period=10, client=None):
        self.logger = logger
        self.grace_period = grace_period
        if client is None:
            try:
                config.load_kube_config()
            except Exception as e:
                msg = f'KubeContext not found or not set. {e}'
                raise Exception(msg)
            self.client = k8s_client.CoreV1Api()
        else:
            self.client = client
        self.kctl = Kubectl(logger=logger)

    def patch_worker(self, name, isnth):
        """
        Patching single worker instance

        @param name: worker name
        @param isnth: node-termination-handler enabled or not
        @return: void
        """
        self.logger.info(f"patch '{name}' worker node")
        # node should be tainted already
        # self.kctl.taint(name)
        self.kctl.drain(name)
        self.logger.info(f'deleting a node...')
        self.logger.info(f'❎ Success: Taint, Cordon and Drain node "{name}"')

    def taint_worker(self, name):
        """
        Patching single worker instance

        @return: void
        """
        self.kctl.taint(name)


    def taint_nodes(self, label_selector=None, node_names=[]):
        """
        Taint nodes with if not yet tainted
        """
        if label_selector:
            node_list = self.client.list_node(label_selector=label_selector)
        elif len(node_names) > 0:
            node_list = self.client.list_node()

        if len(node_list.items) == 0:
            raise ValueError(f"node group '{label_selector}' not found ")

        for node in node_list.items:
            taints = node.spec.taints if node.spec.taints is not None else []
            filtered_taints = list(filter(lambda x: x.key == "key" and x.effect == "NoSchedule", taints))
            node_is_tainted = len(filtered_taints) == 1

            if node_is_tainted:
                continue
            else:
                taints.append({"effect": "NoSchedule", "key": "key", "value": "value"})
                body = {"spec": {"taints": taints}}
                if node.metadata.name in node_names or label_selector:
                    self.client.patch_node(node.metadata.name, body)
                    self.logger.info(f"taint node '{node.metadata.name}'")

    def recycle_nodes(self, label_selector):
        """
        Recycle nodes with if are tainted
        """
        node_list = self.client.list_node(label_selector=label_selector)

        count = 0
        node_tainted_list = []
        for node in node_list.items:
            taints = node.spec.taints if node.spec.taints is not None else []
            filtered_taints = list(filter(lambda x: x.key == "key" and x.effect == "NoSchedule", taints))
            node_is_tainted = len(filtered_taints) == 1
            name = node.metadata.name

            # todo: first remove all non-tainted from the list

            # self.client.delete_node(name, grace_period_seconds=5)
            if node_is_tainted:
                node_tainted_list.append(node)
            else:
                print(f'⚠️  ignore node "{name}", as its not tainted')
                continue

        for node in node_tainted_list:
            print(f"▶️  node should be recyceld: {name}")
            self.kctl.drain(name)
            self.client.delete_node(name, grace_period_seconds=5)
            count += 1
            print(f'‼️ node termination. left {len(node_list.items) - count} to process...')


    def untaint_nodes(self, label_selector=None, node_names=[]):
        """
        Untaint nodes.
        - Select nodes by 'label selector' or with 'node name'
        """
        if label_selector:
            node_list = self.client.list_node(label_selector=label_selector)
        elif len(node_names) > 0:
            node_list = self.client.list_node()

        for node in node_list.items:
            taints = node.spec.taints if node.spec.taints is not None else []
            filtered_taints = list(filter(lambda x: x.key != "key", taints))
            should_have_being_untained = len(taints) - len(filtered_taints) < 2 and len(taints) != len(filtered_taints)
            if len(node_names) > 0 and node.metadata.name in node_names and should_have_being_untained:
                body = {"spec": {"taints": filtered_taints}}
                self.client.patch_node(node.metadata.name, body)
                self.logger.info(f"untaint node '{node.metadata.name}'")
            elif label_selector and should_have_being_untained:
                body = {"spec": {"taints": filtered_taints}}
                self.client.patch_node(node.metadata.name, body)
                self.logger.info(f"untaint node '{node.metadata.name}'")


    def taint_worker_with_python_kubectl_api(self, name):
        """
        Taint worker with extra Tain. Useful in scenarios when we still do need to deploy pods on a node.
        @param name: worker name
        @return: True on success
        """
        self.logger.warning(f'taint worker node {name}')
        taint = k8s_client.V1Taint(effect='NoSchedule', key='experimental')
        tain_body = k8s_client.V1Node(spec=k8s_client.V1NodeSpec(taints=[taint]))
        self.client.patch_node(name, tain_body)
        self.logger.warning("Added taint to the node")

    def info_nodes(self):
        """
        Python client output is too verbose for such a simple case e.g., just to get info about all the nodes
        @return: True on success
        """
        return self.kctl.get_nodes()

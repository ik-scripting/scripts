#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess

EXIT_OK = 0


class Kubectl:

    def __init__(self, logger, process=subprocess):
        self.process = process
        self.logger = logger

    def taint(self, name):
        """
        Python client currently does support taint is just easier to use a command
        @param name: worker name
        @return: True on success
        """
        kubectl_args = [
            'kubectl', 'taint', 'nodes', name,
            'key=value:NoSchedule'
        ]
        self.logger.info(kubectl_args)
        result = self.process.run(kubectl_args)
        if result.returncode != EXIT_OK:
            return False
        return True

    def drain(self, name):
        """
        Python client currently does not support drain.
        @param name: worker name
        @return: True on success
        """
        kubectl_args = [
            'kubectl', 'drain', name,
            '--ignore-daemonsets'
        ]
        kubectl_args.append('--delete-emptydir-data')
        self.logger.info(kubectl_args)
        result = self.process.run(kubectl_args)
        if result.returncode != EXIT_OK:
            return False
        return True

#!/usr/bin/env python
""" 
Read cluster configuration file and resolve to dictionary
"""
import argparse
import json

from py.core.utils import prettify
from py.core.logging import log_debug

class ClusterConfig:
    def __init__(self, exports):
        self.__exports = exports


    def read_remote_cluster_config(self, config, key_name):
        config_dict = {}
        log_debug("looking for key in cluster config: {}".format(key_name))
        
        for environment in config['environments']:
            
            if key_name in environment:
                
                env_config=environment[key_name]

                self.__exports.substitute_export_names(env_options=env_config)

                for item in env_config:
                    config_dict[item['Key']] = item['Value']
                break

        log_debug("found cluster config=" + prettify(config_dict))
        return config_dict
   
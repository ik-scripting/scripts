#!/usr/bin/env python
'''
  Find ExportName 's in configuration sets and replace them with the actual values sourced from cloudformation.
'''

import json

from utils import deserialize, json_serialize, read_template
from logging import log_debug, log_info


class Config:
    def __init__(self, exports):
        self.__exports = exports

    def merge_optional_config(self, mandatory_options, optional_options):
        self.__exports.substitute_export_names(env_options=optional_options)
        result = mandatory_options + optional_options
        return result

    # does the same as load_environment_config only the result is a dictionary.
    def load_environment_dict(self, env_conf_file, profile_config_file=None):
        env_options = self.load_environment_config(env_conf_file=env_conf_file,
                                                   profile_config_file=profile_config_file)
        config = ()
        if len(env_options) > 0:
            config = dict(
                (entry['OptionName'] if 'OptionName' in entry else entry['Key'], entry['Value']) for entry in
                env_options)
        return config


    # environment config is in Beanstalk Option Settings format
    # substitutions occur from cloudformation.
    def load_environment_config(self, env_conf_file, profile_config_file=None):
        env_options = read_template(env_conf_file)

        log_info('Loading environment configuration from {}'.format(env_conf_file))

        if profile_config_file:
            log_info('Including profile config ' + profile_config_file)
            profile_options = json.loads(open(profile_config_file).read())
        else:
            profile_options = []

        self.__exports.substitute_export_names(env_options=env_options)

        merged_options = list(env_options)
        mergable_options = list(profile_options)

        while len(mergable_options) > 0:
            merg_opt = mergable_options.pop(0)
            found = None
            for opt in merged_options:
                if merg_opt == opt:
                    log_debug(
                        "Found duplicate option in profile and environment configuration - please delete one of them : " + json.dumps(
                            opt))
                    found = opt
                    break

            if found is None:
                merged_options.append(merg_opt)

        return merged_options

    def merge_dictionaries(self, *dict_v):
        dict_merge = {}

        for dict_x in dict_v:
            dict_merge.update(dict_x)
        
        return dict_merge

    # resource config is in aws cli format (--generate-cli-skeleton)
    # substitutions occur from values passed in
    def load_resource_config(self, res_conf_file, substitutions):
        log_info('Loading resource configuration from {}'.format(res_conf_file))
        raw_template = read_template(res_conf_file)
        resource_config = self.sub_tokens_json(raw_template, substitutions)

        return resource_config

    def sub_tokens_json(self, json_input, subs):
        log_debug('performing substitutions : ' + str(subs))

        json_unicode = json_serialize(json_input)
        for key in subs:
            val = subs[key]
            # 
            if type(val) == int:
                json_unicode = json_unicode.replace('"{' + key + '}"', str(val))
            else:    
                json_unicode = json_unicode.replace('{' + key + '}', str(val))

        return deserialize(json_unicode)

    def convert_key_value_input_to_dict(self, key_values):
        dictionary = ()
        if key_values:
            dictionary = dict(
                (k.split('=')[0], k.split('=')[1]) for k in key_values)
        return dictionary
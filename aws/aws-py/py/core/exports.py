#!/usr/bin/env python
'''
  Find ExportName 's in configuration sets and replace them with the actual values sourced from cloudformation.
'''

from logging import log_info


class Exports:
    def __init__(self, session):
        self.__session = session

    def substitute_export_names(self, env_options):
        needs_lookup = False
        for option in env_options:
            if 'ExportName' in option:
                needs_lookup = True
                break

        if not needs_lookup:
            print 'No export name lookups required.'
            return env_options

        all_export_names = []

        # if any of the option settings has an "ExportName" in it then subsitute with the export value
        for option in env_options:
            if 'ExportName' in option:
                if len(all_export_names) == 0:
                    # lazy load a hash of all the exports from all cloudformation stacks
                    # handling large paginated result sets
                    all_export_names = self.__fetch_exports()

                export_name = option['ExportName']

                if export_name in all_export_names:
                    value = all_export_names[export_name]
                    log_info('Substituting ExportName: ' + export_name + ' with actual value ' + value)
                    option.pop('ExportName', None)
                    option['Value'] = value
                else:
                    raise EnvironmentError("Resource with ExportName: {} not found \n"
                                           "Please check cloudfromation template outputs".format(export_name))

    def extract_exports(self):
        return self.__fetch_exports()

    def __fetch_exports(self):
        all_export_names = {}
        next_token = None

        cf_client = self.__session.current.client('cloudformation')

        while True:

            # use page token if last result had one
            if next_token is None:
                _exports = cf_client.list_exports()
            else:
                _exports = cf_client.list_exports(
                    NextToken=next_token
                )

            # translate export names into our own dictionary
            for exportDict in _exports['Exports']:
                all_export_names[exportDict['Name']] = exportDict['Value']

            # get the token for the next page if it exists
            # if no page token then we are done
            if 'NextToken' in _exports:
                next_token = _exports['NextToken']
            else:
                break
        return all_export_names

    # Recursive function will walk the 'options' structure until it finds an 'ExportName' and will substitute it
    # with the value from 'all_export_names'.
    # Export names must be defined as a python dictionary in form:
    # {
    #    "ExportName": "export_name_to_replace"
    # }
    # On subsituting value the entire dictionary object will be replaced with the export value
    def swap_exports(self, all_export_names, current_option, parent_key=None, parent_option=None):
        if isinstance(current_option, dict):
            for key in current_option:
                # print key
                sub_value = self.swap_exports(all_export_names, current_option[key], key, current_option)

                if sub_value:
                    log_info('substituting option : \'' + parent_key + '\' to ' + sub_value)
                    parent_option[parent_key] = sub_value
            return

        if isinstance(current_option, list):
            for list_opt in current_option:
                swap_exports(all_export_names, list_opt, None, current_option)
            return

        if 'ExportName' == parent_key:
            return all_export_names[current_option]

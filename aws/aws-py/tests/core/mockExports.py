#!/usr/bin/env python
'''
  Find ExportName 's in configuration sets and replace them with the actual values sourced from cloudformation.
'''


class MockExports:
    def __init__(self, swaps=None):
        self._swaps = swaps or {}

    def substitute_export_names(self, env_options):
        for env in env_options:
            if 'ExportName' in env:
                key = env['OptionName'] if 'OptionName' in env else env['Key']
                env['Value'] = self._swaps[key]

    def extract_exports(self):
        pass

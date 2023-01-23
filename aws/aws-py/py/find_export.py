#!/usr/bin/env python
'''
  Find ExportName 's in configuration sets and replace them with the actual values sourced from cloudformation.
  Usage example
  chmod +x find_export.py
  export URL=$(./find_export.py --get-export "<project-name>-srv-nonprod-enterprise-services-app-load-balancer-feature-ecs-deploy::LoadBalancerUrl")
'''

import argparse

parser = argparse.ArgumentParser(description='Process Arguments.')
parser.add_argument('--get-export', type=str,   required=True, dest='export_name')


def find_export_value(export_name):


    session = Session.factory()
    export = Exports(session)

    cf_client = session.current.client('cloudformation')
    all_export_names = export.extract_exports()


    for exportValue in all_export_names:
        if exportValue == export_name:
            result = all_export_names[exportValue]
            return result

    raise ValueError("Could not find export name " + export_name)


if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from py.core.session import Session
    from py.core.config import Config
    from py.core.exports import Exports
    from py.core.utils import enablePrint, blockPrint
    blockPrint()
    args = parser.parse_args()

    result=find_export_value(args.export_name)

    enablePrint()

    print(result)

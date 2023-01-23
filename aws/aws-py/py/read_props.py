#!/usr/bin/env python

import argparse
import json
# TODO: move to deploy_scripts
parser = argparse.ArgumentParser(description='Process Arguments.')
parser.add_argument('environments_file', type=str)
parser.add_argument('--filter', type=str, required=True, dest='filter', help='filter property objects on key=value')
parser.add_argument('--fetch', type=str, required=True, dest='fetch', help='retrieve value from property object')

if __name__ == "__main__":
    args = parser.parse_args()

    filter = args.filter.split('=')
    key = filter[0]
    value = filter[1]

    environments = json.loads(open(args.environments_file).read())

    for environment in environments:
        if environment[key] == value:
            print(environment[args.fetch])
            break

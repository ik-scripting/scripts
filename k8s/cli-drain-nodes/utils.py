#!/usr/bin/env python3

import json, os, yaml
from pathlib import Path

def json_prettify(data):
    return json.dumps(data, indent=4, default=str)


def load_json(data):
    return json.loads(data)


def read_from_json_file(file):
    return json.loads(open(file).read())


def read_from_yml_file(file):
    return yaml.safe_load(open(file))

def yaml_prettify(data):
  return yaml.dump(data, default_flow_style=False, default_style='' )

# utils.write_to_file("elbs.json", utils.json_prettify({}))
def write_to_file(file, data):
    Path(os.path.dirname(file)).mkdir(parents=True, exist_ok=True)
    f = open(f'{file}', "w")
    f.write(data)
    f.close()


def file_directory(file):
    return os.path.dirname(file)

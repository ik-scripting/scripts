#!/usr/bin/env python

import json
import os


def json_serialize(data):
    return json.dumps(data, indent=4, sort_keys=False)


def deserialize(data):
    return json.loads(data)


def read_template(file):
    return json.loads(open(file).read())


def find_directory(source):
    return os.path.dirname(os.path.abspath(source))


def read_nested():
    return lambda o: o.__dict__

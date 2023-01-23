#!/usr/bin/env python

import json
import os, sys


def json_serialize(data):
    return json.dumps(data, indent=4, sort_keys=False)

def prettify(dict):
    return json.dumps(dict, indent=4, sort_keys=False, default=str)

def deserialize(data):
    return json.loads(data)

def read_template(file):
    return json.loads(open(file).read())

def read_file(file):
    return open(file).read()

def find_directory(source):
    return os.path.dirname(os.path.abspath(source))


def read_nested():
    return lambda o: o.__dict__


def blockPrint():
    sys.stdout = open(os.devnull, 'w')


def enablePrint():
    sys.stdout = sys.__stdout__

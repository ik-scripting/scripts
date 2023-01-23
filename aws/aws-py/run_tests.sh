#!/bin/bash

set -e

# execute tests
#python -m unittest discover -t tests
coverage run --source py -m unittest discover -t tests
coverage report -m

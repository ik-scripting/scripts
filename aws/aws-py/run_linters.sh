#!/bin/bash


echo "+++Pylint Start (uses '.pylintrc')+++"
# execute style check
pylint py
echo "---Pyling End---"

echo "+++Flake Start (uses 'setup.cfg')++"
flake8
echo "---Flake End---"

echo "Currently there is no Failures. Please Fix linter errors As you do development"

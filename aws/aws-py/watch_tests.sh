#!/bin/bash
# pull in all requirements
pip install -r py/requirements.txt
pip install -r tests/requirements.txt

# execute tests
watch -n 10 python -m unittest discover -t tests

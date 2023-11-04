#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# TODO: document what it does
# [ ] Move to args parser as it clear
# ./tfm-import.py --help
from cmd.terraform import tfmwrapper
if __name__ == '__main__':
    tfmwrapper.extract_what_to_import()
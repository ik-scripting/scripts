#!/usr/bin/env python

import boto3


def create_context(region):
    session = boto3.session.Session(region_name=region)
    esr = session.client('ecr')
    return (esr)

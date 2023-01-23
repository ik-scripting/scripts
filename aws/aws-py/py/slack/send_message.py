#!/usr/bin/env python

import os
from os import sys, path
import argparse

from slackclient import SlackClient

parser = argparse.ArgumentParser(description='Process Arguments.')
parser.add_argument('--message', type=str, required=True, dest='message')
parser.add_argument('--channel', type=str, required=True, dest='channel')

if __name__ == '__main__' and __package__ is None:
    """Send slack message"""
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

    args = parser.parse_args()

    slack_token = os.environ["SLACK_API_TOKEN"]
    sc = SlackClient(slack_token)

    sc.api_call(
        "chat.postMessage",
        channel=args.channel,
        text=args.message
    )

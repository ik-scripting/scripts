#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import requests, json

text = 'To EKS migrate, or not to EKS migrate! 🤔'

class Slack:

    def __init__(self, ssm_token_id, ssm_client, channel, username):
        self.channel = channel
        self.username = username
        result = ssm_client.get_parameter(
            Name=ssm_token_id,
            WithDecryption=True
        )
        self.token = result['Parameter']["Value"]


    def post_message_to_slack(self, msg, ctx=None):
        dt = datetime.now().replace(second=0, microsecond=0)
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{msg}. ⏳ {dt}"
                }
            }
        ]
        if ctx != None:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{ctx}"
                }
            })

        result = requests.post('https://slack.com/api/chat.postMessage', {
            'token': self.token,
            'channel': self.channel,
            'text': text,
            'username': self.username,
            'blocks': json.dumps(blocks) if blocks else None
        }).json()

        if result['ok'] == False:
            raise Exception('error when sending slack notification!!!!!')

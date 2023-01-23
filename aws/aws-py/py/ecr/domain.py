#!/usr/bin/env python


class Policy:
    def __init__(self, json):
        self.Version = json['Version']
        self.Statement = [Statement.factory(val) for val in json['Statement']]

    @staticmethod
    def factory(dct):
        return Policy(dct)

    def __str__(self):
        return self.__dict__


class Action:
    def __init__(self, json):
        self.actions = [str(val) for val in json]

    @staticmethod
    def factory(dct):
        return Action(dct)

    def __str__(self):
        return str(self.actions)


class Statement:
    def __init__(self, json):
        self.Sid = json['Sid']
        self.Effect = json['Effect']
        self.Principal = json['Principal']
        self.Action = Action.factory(json['Action']).actions

    @staticmethod
    def factory(dct):
        return Statement(dct)

    def update(self, sid, accid):
        self.Sid = str(self.Sid).format(statement_id=sid)
        self.Principal['AWS'] = str(self.Principal['AWS']).format(principal=accid)

    def __str__(self):
        return json_serialize({
            'Sid': self.Sid,
            'Effect': self.Effect,
            'Principal': self.Principal,
            'Action': self.Action
        })

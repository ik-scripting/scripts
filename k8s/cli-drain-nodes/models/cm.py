# -*- coding: utf-8 -*-

class CMDs:

    def __init__(self, data):
        self.data = data
        self.account = Account(self.data['account_id'], self.data["accounts"])
        self.migrate_asg = MigrageASG(self.data['commands']['migrage_asg'])
        self.taints = Taints(self.data['commands']['taints'])
        self.recycle = Recycle(self.data['commands']['recycle'])
        self.slack  = Slack(self.data['slack'])

    @staticmethod
    def factory(data):
        return CMDs(data)

    def __str__(self):
        return f'Taints:: {self.taints}. Migrate ASG:: {self.migrate_asg}. Account:: {self.account.account_name}'

    def __repr__(self):
        return self.__str__()

class Account:
    def __init__(self, account_id, data) -> None:
        self.account_name = data[account_id]
        self.account_id = account_id

    def __str__(self):
        return f'id: {self.account_id}({self.account_name})'

    def __repr__(self):
        return self.__str__()

class Slack:
    def __init__(self, data) -> None:
        self.channel = data.get('channel')
        self.ssm_token_id = data.get('ssm_token_id')
        self.name = data.get('name')

    def __str__(self):
        return f'channel: {self.channel}, increment: {self.name}'

    def __repr__(self):
        return self.__str__()

class MigrageASG:
    def __init__(self, data) -> None:
        self.asg_name = data.get('asg_name')
        self.scaledown_increment = data.get('scaledown_increment', 1)
        self.nth = data.get('nth', False)

    def __str__(self):
        return f'asg_name: {self.asg_name}, increment: {self.scaledown_increment}, nth: {self.nth}'

    def __repr__(self):
        return self.__str__()

class Taints:

    def __init__(self, data) -> None:
        self.asg_name = data.get('asg_name', '')
        self.label_selector = data.get('label_selector', '')
        self.taint_asg = data.get('taint_all_nodes', False)
        self.untaint_asg = data.get('untaint_all_nodes', False)
        self.legacy = data.get('legacy', False)
        if self.taint_asg == True and self.untaint_asg == True:
            raise Exception("Taint or Untain Nodes in ASG. Not both.")
        if self.asg_name == '' and self.label_selector == '':
            raise Exception("ASG name or label selector must be spcified.")

    def __str__(self):
        return f'asg_name: {self.asg_name}, taint: {self.taint_asg}, untaint: {self.untaint_asg}'

    def __repr__(self):
        return self.__str__()

class Recycle:

    def __init__(self, data) -> None:
        self.label_selector = data.get('label_selector', '')

    def __str__(self):
        return f'selector: {self.label_selector}'

    def __repr__(self):
        return self.__str__()

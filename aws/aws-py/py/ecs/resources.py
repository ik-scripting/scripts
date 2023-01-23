"""Messages"""
WAITERMSG = {
    'deregistration': '\nTime to wait is `2x{}` seconds for current Target Group.',
    'message': 'Wait untill other targets deregistered.\nTo make sure system is in working state.',
    'inconsistent': 'Registration COMPLETE with instances left in incosistent state. Current targets: {}',
    'failed': 'Failed to deploy task. {}. Number of `{}` targets should be equal `{}`',
    'complete': ' Registration COMPLETE. Number of `{}` targets is equal `{}`.',
    'recovertime': '\nAllowing `{}` seconds of time to recover...',
    'state': 'Current State: `{}` ...',
    'taskstatus': ' Status: {}.\n Task: {}.\n==',
    'taskrunning': ' Specified `{}` Task is RUNNING.',
    'validationfailed': '\n=====\nNew Task Registration failed deployment validation\n=====\n'
}

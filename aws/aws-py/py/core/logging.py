from os import getenv

__logging = getenv('LOGGING')

if __logging is None:
    __logging = 'INFO'


def log_debug(message):
    if __logging == 'DEBUG':
        print(message)


def log_info(message):
    if __logging == 'INFO':
        print(message)


def set_log_level(level):
    global __logging
    __logging = level

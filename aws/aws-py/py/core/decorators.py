#!/usr/bin/env python
'''
https://realpython.com/blog/python/primer-on-python-decorators/
'''
from functools import wraps
from py.core.logging import log_info


def log_entry_and_exit(func):
    """
    Function decorator logging entry + exit and parameters of functions.

    Entry and exit as logging.info, parameters as logging.DEBUG.
    """

    @wraps(func)
    def wrapper(*func_args, **func_kwargs):
        func_name = func.__name__
        log_info('\n')
        log_info('Entering {}()...'.format(func_name))

        arg_names = func.func_code.co_varnames[:func.func_code.co_argcount]
        args = func_args[:len(arg_names)]
        defaults = func.func_defaults or ()
        args = args + defaults[len(defaults) - (func.func_code.co_argcount - len(args)):]
        params = zip(arg_names, args)
        args = func_args[len(arg_names):]
        if args: params.append(('args', args))
        if func_kwargs: params.append(('params', func_kwargs))
        message = '(' + ', '.join('%s = %r' % p for p in params) + ' )'
        log_info("{}".format(message))
        out = func(*func_args, **func_kwargs)
        # log_info('Done running {}()'.format(func_name))
        log_info("\n")
        return out
    return wrapper

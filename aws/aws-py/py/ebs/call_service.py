#!/usr/bin/env python
'''
 Make a call to endpoint.
 Can be  introduces as fully platform test
'''
import json

from httplib2 import Http


def __build_headers():
    return {'Connection': 'Close',
            'Accept': 'application/json'}


def call_service(targetUrl):
    http_obj = Http(cache=None, timeout=1, disable_ssl_certificate_validation=True)
    (resp, content) = http_obj.request(uri=targetUrl, method='GET', headers=__build_headers())
    return {'health_app': resp.status, 'status_app': json.loads(content.decode("utf-8"))['status']}

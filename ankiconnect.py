# https://github.com/FooSoft/anki-connect

import json
import urllib2

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, version=6, **params):
    requestJson = json.dumps(request(action, **params))
    response = json.load(urllib2.urlopen(urllib2.Request('http://localhost:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']
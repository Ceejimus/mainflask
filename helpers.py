"""helper functions"""
import sys
from flask import json

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def json_response(response, status_code=200):
    return json.dumps(response), status_code, { 'ContentType':'application/json' }

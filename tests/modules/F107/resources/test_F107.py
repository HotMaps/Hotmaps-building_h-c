import json
import requests
import os
import sys

sys.path.append( os.path.join( os.path.dirname(os.path.abspath(__file__)), "..", "..", ".." ) )
from test_settings import base_url

def test_example_post():
    """
    This is an example method on how to do unit test on your API, you need to execute this using py.test in order to work
    It will query the app and compare it with an already existing JSON file located in payload.txt

    $ pytest test_example.py
    """
    url = base_url + "/buildinghc/f107"

    ######

    path = os.path.dirname( os.path.abspath( __file__ ) )

    # payload which is sent to server
    payload = None
    with open( os.path.join(path,"payload.json"), "r") as fd:
        payload = json.load(fd)

    # result which we expect
    result = None
    with open( os.path.join(path,"result.json"), "r") as fd:
        result = json.load(fd)

    # send payload to server
    output = requests.post( url, json=payload)

    # check if server answer matches out expectation
    assert output.json() == result


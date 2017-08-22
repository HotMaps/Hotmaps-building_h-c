import json
import requests
import codecs

import os
import sys
import glob

def assert_equal_json(url, f_payload, f_result):
    # payload which is sent to server
    payload = json.load(codecs.open(f_payload, "r", "utf-8-sig"))

    # result which we expect
    result = json.load(codecs.open(f_result, "r", "utf-8-sig"))

    # send payload to server
    output = requests.post( url, json=payload)

    # check if server answer matches out expectation
    assert output.json() == result

def gen_tests(name, path, url, method):
    cnt = 0
    tests = []

    for f in glob.glob( os.path.join(path,"payload*.json") ):
        f_payload = f
        f_result = f_payload.replace( 'payload', 'result' )

        test_method_str = "def test_%s_%s(): %s('%s', '%s', '%s')"%\
                (name, cnt, method, url, f_payload, f_result)

        tests.append( test_method_str )
        cnt += 1

    return tests

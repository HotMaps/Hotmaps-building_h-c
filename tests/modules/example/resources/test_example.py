import json
import requests
import os

def test_example_post():
    """
    This is an example method on how to do unit test on your API, you need to execute this using py.test in order to work
    It will query the app and compare it with an already existing JSON file located in payload.txt
    """
    # TODO: set up the URL of your localhost (specially the port)
    url = "http://localhost:9005/api/v1/example/hello/world"

    payload = "{\r\n  \"payload\": {\r\n    \"text\": \"This is a test\"\r\n  }\r\n}"
    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache",
        'postman-token': "d188c7bd-5556-d8e0-33e2-f4c1d1abd817"
    }

    output = requests.request("POST", url, data=payload, headers=headers)

    json_file = os.path.join(os.path.dirname(__file__), "payload.txt")

    json_str = open(json_file).read()

    expected_output = json.loads(json_str)

    assert output.json() == expected_output
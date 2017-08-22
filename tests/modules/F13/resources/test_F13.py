import sys
import os

sys.path.append( os.path.join( os.path.dirname(os.path.abspath(__file__)), "..", "..", ".." ) )
from test_settings import base_url
from test_common import assert_equal_json, gen_tests

url = base_url + "/buildinghc/f13"

path = os.path.dirname( os.path.abspath( __file__ ) )
name = os.path.splitext( os.path.basename(__file__) )[0]

for test in gen_tests(\
        name,\
        path,\
        url,\
        'assert_equal_json' ):
    exec( test )

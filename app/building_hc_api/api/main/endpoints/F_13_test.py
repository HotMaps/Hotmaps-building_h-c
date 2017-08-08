import logging

from flask import request
from flask_restplus import Resource
from building_hc_api.api.restplus import api

import os, sys

print( "PATH: ", sys.path )

from osgeo import gdal


path = '/data/src'
if path not in sys.path:
    sys.path.append(path)
print( "SYS.PATH", sys.path )
from FEAT.F13_district_heating_potential import F_13 as test_run

log = logging.getLogger(__name__)

ns = api.namespace('test', description='Operations related to F13')

@ns.route('/f13_test')
class F13Test(Resource):
    def get(self):
        ret_value = test_run.execute('', '', '')
        return ret_value #'test f_13'

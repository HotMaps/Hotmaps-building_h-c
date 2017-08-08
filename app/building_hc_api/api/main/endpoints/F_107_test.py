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
from FEAT.F107_scaling_hdm import F_107 as test_run

log = logging.getLogger(__name__)

ns = api.namespace('test', description='Operations related to F107')

@ns.route('/f107_test')
class F107Test(Resource):
    def get(self):
        ret_value = test_run.execute('','','')
        return ret_value #'test f_107'


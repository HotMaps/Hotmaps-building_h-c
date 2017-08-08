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
from FEAT.F14_individual_heat_supply_costs_per_building import F_14 as test_run

log = logging.getLogger(__name__)

ns = api.namespace('test', description='Operations related to F14')

@ns.route('/f14_test')
class F13Test(Resource):
    def get(self):
        ret_value = test_run.execute('', '', '')
        return ret_value #'test f_14'


import logging

from flask import request
from flask_restplus import Resource
#from building_hc_api.api.main.serializers import hello_world
from building_hc_api.api.restplus import api
#from ... import F_13 as test_run # calculation module
#from C:\Users\fritz\Documents\GitHub\HotMaps-building_h-c\src\FEAT\F13_district_heating_potential
#from src.FEAT.F63_bottomup_heat_density_map import F_63 as test_run


log = logging.getLogger(__name__)

ns = api.namespace('test', description='Operations related to F63')

@ns.route('/f63_test')
class F13Test(Resource):
    def get(self):
        ret_value = test_run.execute('', '', '')
        return ret_value #'test f_63'




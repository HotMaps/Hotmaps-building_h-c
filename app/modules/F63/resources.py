"""
This is the list of method that will be used by the api
"""

import logging

import os

from extensions.api.api import Namespace
from flask_restplus_patched import Resource

from . import schemas, parameters
from ..common import custom_fields

from ..common.FEAT.F63_bottomup_heat_density_map import F_63

log = logging.getLogger(__name__)
api = Namespace('buildinghc', 'building hc')

@api.route('/f63')
class F63(Resource):
    @api.response(schemas.F63Schema())
    @api.parameters(parameters.F63Parameter())

    def post(self, args):
        payload = args['payload']

        # text, demand_value need to be defined in schema
        spec_demand_csv = payload['spec_demand_csv']
        building_strd_info_csv = payload['building_strd_info_csv']
        inShapefile = payload['inShapefile']

        try:
            f_63_ret = F_63.execute(spec_demand_csv, building_strd_info_csv, inShapefile)
        except:
            f_63_ret = {"attention": "something went wrong"}

        # response need to be defined in schema
        return {"response": f_63_ret }

    @api.response(schemas.F63Schema())
    def get(self):
        return {"text": "hi 63 (get)"}


"""
This is the list of method that will be used by the api
"""

import logging

import os

from extensions.api.api import Namespace
from flask_restplus_patched import Resource

from . import schemas, parameters
from ..common import custom_fields

from ..common.FEAT.F107_scaling_hdm import F_107

log = logging.getLogger(__name__)
api = Namespace('buildinghc', 'building hc')

@api.route('/f107')
@api.route('/Heat-Density-Maps/Scaling-HDM')
class F107(Resource):
    @api.response(schemas.F107Schema())
    @api.parameters(parameters.F107Parameter())

    def post(self, args):
        payload = args['payload']

        #  demand_value need to be defined in schema
        demand_value = payload['updated_demand_value']

        path = "/data/modules/common"
        output_dir = path + os.sep + 'Outputs'
        outRasterPath = output_dir + os.sep + 'F107_' + 'scaled_hdm.tif'

        try:
            f_107_ret = F_107.execute(demand_value, output_dir, outRasterPath)
        except:
            f_107_ret = {"attention": "something went wrong"}

        # response need to be defined in schema
        return {"response": f_107_ret}




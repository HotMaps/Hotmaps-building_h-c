"""
This is the list of method that will be used by the api
"""

import logging

import os

from extensions.api.api import Namespace
from flask_restplus_patched import Resource

from . import schemas, parameters
from ..common import custom_fields

from ..common.FEAT.F13_district_heating_potential import F_13

log = logging.getLogger(__name__)
api = Namespace('buildinghc', 'building hc')

@api.route('/f13')
@api.route('/District-Heating-Potential/energetic_threshold')
class F13(Resource):
    @api.response(schemas.F13Schema())
    @api.parameters(parameters.F13Parameter())

    def post(self, args):
        payload = args['payload']
    
        path = "/data/modules/common"
        output_dir = path + os.sep + 'Outputs'
        outRasterPath = output_dir + os.sep + 'F13_' + 'Pot_AT_TH30.tif'

        try:
            f_13_ret = F_13.execute(outRasterPath)
        except:
            f_13_ret = {"attention": "something went wrong"}

        # text, response need to be defined in schema
        return {"response":  f_13_ret }



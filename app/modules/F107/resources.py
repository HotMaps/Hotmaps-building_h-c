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
class F107(Resource):
    @api.response(schemas.F107Schema())
    @api.parameters(parameters.F107Parameter())

    def post(self, args):
        payload = args['payload']

        # text, demand_value need to be defined in schema
        text = payload['text']
        demand_value = payload['demand_value']

        # data and source should not be in same directory...
        path = '/data/data/' # does not exist (yet). needs to be copied by Dockerfile
        output_dir = path + os.sep + 'Outputs'
        outRasterPath = output_dir + os.sep + 'F107_' + 'scaled_hdm.tif'

        try:
            f_107_ret = F_107.execute(demand_value, output_dir, outRasterPath)
        except:
            f_107_ret = None

        # text, response need to be defined in schema
        return {"text": "posted %s, %d to f107"%( text, demand_value ), "response": f_107_ret }

    @api.response(schemas.F107Schema())
    def get(self):
        return {"text": "hi 107 (get)"}


"""
This is the list of method that will be used by the api
"""

import logging

import os

from extensions.api.api import Namespace
from flask_restplus_patched import Resource

from . import schemas, parameters
from ..common import custom_fields

from ..common.FEAT.F14_individual_heat_supply_costs_per_building import F_14

log = logging.getLogger(__name__)
api = Namespace('buildinghc', 'building hc')

@api.route('/f14')
class F14(Resource):
    @api.response(schemas.F14Schema())
    @api.parameters(parameters.F14Parameter())

    def post(self, args):
        payload = args['payload']
        
        
        interest_rate = payload['interest_rate']
        lifetime = payload['lifetime']
        ##Information from selected area
        
        user_input_nuts0 = payload['nuts0']
        user_input_nuts3 = payload['nuts3']
        population = payload['population']

        #user input
        sel_building_energy_demand= payload['building_energy_demand']
        sel_building_heat_load = payload['building_heat_load']

        try:
            f_14_ret = F_14.execute(interest_rate, lifetime, user_input_nuts0, user_input_nuts3, population, sel_building_energy_demand, sel_building_heat_load)
        except:
            f_14_ret = {"attention": "something went wrong"}

        # response need to be defined in schema
        return {"response": f_14_ret }

    @api.response(schemas.F14Schema())
    def get(self):
        return {"text": "hi 14 (get)"}


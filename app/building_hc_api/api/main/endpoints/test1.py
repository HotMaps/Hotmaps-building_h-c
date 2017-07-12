import logging

from flask import request
from flask_restplus import Resource
from building_hc_api.api.main.serializers import hello_world
from building_hc_api.api.restplus import api
#from src.FEAT.F14_individual_heat_supply_costs_per_building import F_14

log = logging.getLogger(__name__)

ns = api.namespace('test', description='test operation from Sara')


@ns.route('/world/<string:name>')
@api.response(404, 'reason for an error2')
class PopulationDensityByNuts(Resource):

    @api.marshal_with(hello_world)
    def get(self, name):
        """
        Try to run TUWs first module
        :param param:
        :return:
        """
        return {'asdf': name}



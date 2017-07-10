import logging

from flask import request
from flask_restplus import Resource
from building_hc_api.api.main.serializers import hello_world
from building_hc_api.api.restplus import api

log = logging.getLogger(__name__)

ns = api.namespace('hello', description='Operations related to hello world')


@ns.route('/world/<string:name>')
@api.response(404, 'Hello world not found.')
class PopulationDensityByNuts(Resource):

    @api.marshal_with(hello_world)
    def get(self, name):
        """
        Returns a population density for specific nuts
        :param param:
        :return:
        """
        return {'hello': name}



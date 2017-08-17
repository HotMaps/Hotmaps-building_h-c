"""
The schemas that will be taken as base by the api or the parameters, they are using marshmallow technology
"""

from flask_restplus_patched import Schema
from flask_marshmallow import base_fields
from ..common import schemas as commonSchema

class F14Schema(Schema):
    response = base_fields.Dict()
    interest_rate = base_fields.Float()
    lifetime = base_fields.Integer()

    ##Information from selected area
    nuts0 = base_fields.String()
    nuts3 = base_fields.String()
    population = base_fields.Integer()

    #user input
    building_energy_demand= base_fields.Float()
    building_heat_load = base_fields.Float()

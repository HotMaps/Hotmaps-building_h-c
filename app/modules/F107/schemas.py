"""
The schemas that will be taken as base by the api or the parameters, they are using marshmallow technology
"""

from flask_restplus_patched import Schema
from flask_marshmallow import base_fields
from ..common import schemas as commonSchema

class F107Schema(Schema):
    #text = base_fields.String()
    #demand_value = base_fields.Integer()
    #response = base_fields.Dict()
    updated_demand_value = base_fields.Integer()
    otput_dir = base_fields.String()
    outRasterPath = base_fields.String()
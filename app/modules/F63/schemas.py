"""
The schemas that will be taken as base by the api or the parameters, they are using marshmallow technology
"""

from flask_restplus_patched import Schema
from flask_marshmallow import base_fields
from ..common import schemas as commonSchema

class F163Schema(Schema):
    spec_demand_csv = base_fields.String()
    building_strd_info_csv = base_fields.String()
    inShapefile = bbase_fields.String()

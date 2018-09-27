"""
The schemas that will be taken as base by the api or the parameters, they are using marshmallow technology
"""

from flask_restplus_patched import Schema
from flask_marshmallow import base_fields
from ..common import schemas as commonSchema

class F23Schema(Schema):
    case_study = base_fields.List()
    output_dir = base_fields.String()
    response = base_fields.Dict()
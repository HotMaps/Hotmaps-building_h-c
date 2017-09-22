# encoding: utf-8
# pylint: disable=wrong-import-order
"""
Input arguments (Parameters) for grid resources RESTful API
"""

from flask_restplus_patched import Parameters
from flask_marshmallow import base_fields
from . import schemas

class F14Parameter(Parameters):
    payload = base_fields.Nested(schemas.F14Schema())
    payload.metadata['location'] = 'json'

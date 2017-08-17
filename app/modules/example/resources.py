"""
This is the list of method that will be used by the api
"""

import logging

from extensions.api.api import Namespace
from flask_restplus_patched import Resource

from . import schemas, parameters
from ..common import custom_fields

log = logging.getLogger(__name__)
api = Namespace(custom_fields.EXAMPLE, description=custom_fields.EXAMPLE_DESCRIPTION)

@api.route('/hello/world')
class Example(Resource):
    """
    Basic example class
    """
    @api.response(schemas.ExampleSchema())
    @api.parameters(parameters.ExampleParameter())

    def post(self, args):
        """
        a basic post request
        :param args:
        a payload containing a text
        :return:
        the text
        """
        payload = args[custom_fields.PAYLOAD]
        text = payload.get(custom_fields.TEXT)
        output = {
            custom_fields.TEXT: text
        }
        return output
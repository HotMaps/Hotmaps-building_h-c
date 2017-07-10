from flask_restplus import fields
from building_hc_api.api.restplus import api



hello_world = api.model('Population density', {
    'hello': fields.String(),
})


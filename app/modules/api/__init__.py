# encoding: utf-8
"""
Launch the app
======================================
"""
from flask import Blueprint
from extensions import api

def init_app(app, **kwargs):
    # pylint: disable=unused-argument
    api_blueprint = Blueprint('api', __name__, url_prefix='/api/v'+api.version[0:1]) #TODO: if you want to modify the name of the api change the url_prefix (for now it is /api/v1)
    api.init_app(api_blueprint)
    app.register_blueprint(api_blueprint)

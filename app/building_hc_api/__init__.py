import logging.config
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, Blueprint
from building_hc_api import settings
from building_hc_api.api.main.endpoints.test1 import ns as test1_alias
#from building_hc_api.api.main.endpoints.test1 import nste as main_population_namespace
from building_hc_api.api.restplus import api

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logging.conf')
logging.config.fileConfig(log_file_path)
log = logging.getLogger(__name__)

# methods
def configure_app(flask_app):
    flask_app.config['DEBUG'] = settings.FLASK_DEBUG
    flask_app.config['SECRET_KEY'] = settings.FLASK_SECRET_KEY
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP


def initialize_app(flask_app):
    configure_app(flask_app)

    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    api.add_namespace(test1_alias)
    flask_app.register_blueprint(blueprint)


def create_app():
    """
    Create app instance
    """
    app = Flask(__name__)
    
    initialize_app(app)

    return app

# encoding: utf-8
# pylint: disable=invalid-name,wrong-import-position
"""
Extensions setup
================

Extensions provide access to common resources of the application.

Please, put new extension instantiations and initializations here.
"""

from flask_cors import CORS
cross_origin_resource_sharing = CORS()

from sqlalchemy_utils import force_auto_coercion, force_instant_defaults
force_auto_coercion()
force_instant_defaults()

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(session_options={'autocommit': True})

from flask_marshmallow import Marshmallow
marshmallow = Marshmallow()

from . import api

import logging.config
import sys
import os
import settings
import modules

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask
from flask_cors import CORS
from extensions.api import api
from extensions import db

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logging.conf')
logging.config.fileConfig(log_file_path)
log = logging.getLogger(__name__)
logging.getLogger('flask_cors').level = logging.DEBUG


# methods
def configure_app(flask_app):
    flask_app.config['DEBUG'] = settings.FLASK_DEBUG
    # flask_app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME
    flask_app.config['SECRET_KEY'] = settings.FLASK_SECRET_KEY
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP


def initialize_app(flask_app):
    configure_app(flask_app)

    for extension in (
            cross_origin_resource_sharing,
            db,
            marshmallow,
            api,
    ):



        extension.init_app(flask_app)
    flask_app.extensions['migrate'] = AlembicDatabaseMigrationConfig(db, compare_type=True)

def create_app():
    """
    Create app instance
    """
    app = Flask(__name__)

    initialize_app(app)

    CORS(app, resources={r"/api/*": {"origins": "http://hotmaps.hevs.ch"}})

    modules.init_app(app)

    return app


class AlembicDatabaseMigrationConfig(object):
    """
    Helper config holder that provides missing functions of Flask-Alembic
    package since we use custom invoke tasks instead.
    """

    def __init__(self, database, directory='migrations', **kwargs):
        self.db = database
        self.directory = directory
        self.configure_args = kwargs
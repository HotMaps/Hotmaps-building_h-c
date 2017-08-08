# Flask settings
#FLASK_SERVER_NAME = '0.0.0.0:80'
#FLASK_SERVER_NAME = '0.0.0.0:5000'
FLASK_DEBUG = True  # Do not use debug mode in production
FLASK_SECRET_KEY = 'test-secret-key'

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# SQLAlchemy settings
# this is not used in our projet, but you can use them if you need to interact with a DB,
# we are keeping it in order to avoid useless warnings
SQLALCHEMY_DATABASE_URI = None #this is the uri for your DB
SQLALCHEMY_TRACK_MODIFICATIONS = False

#TODO: list the modules you are using here so they can be launched by the api
ENABLED_MODULES = (
    'example', #TODO: remove the example module
    'api',
)
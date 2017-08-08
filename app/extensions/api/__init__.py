import traceback, logging, settings

from sqlalchemy.orm.exc import NoResultFound

from .api import Api

log = logging.getLogger(__name__)

#TODO: name your API
api = Api(version='1.0',
          title='Example  API',
          description='This is an example of API.'
)

@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)

    if not settings.FLASK_DEBUG:
        return {'message': message}, 500


@api.errorhandler(NoResultFound)
def database_not_found_error_handler(e):
    log.warning(traceback.format_exc())
    return {'message': 'A models result was required but none was found.'}, 404
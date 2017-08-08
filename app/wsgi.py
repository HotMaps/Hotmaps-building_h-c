#this is used to launch the project

from extensions import create_app, log

application = create_app()
log.info(application)
if __name__ == "__main__":
    application.run()


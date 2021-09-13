from celery import Celery
from flasgger import Swagger
from flask import Flask
from werkzeug.debug import DebuggedApplication
from werkzeug.middleware.proxy_fix import ProxyFix

from bitcoinstore.api.products import products
from bitcoinstore.api.reservations import reservations
from bitcoinstore.extensions import db
from bitcoinstore.extensions import debug_toolbar
from bitcoinstore.extensions import flask_static_digest
from bitcoinstore.model.reservation import FungibleReservation, NonFungibleReservation
from bitcoinstore.page.views import page
from bitcoinstore.tasks import expire_reservation


def create_celery_app(app=None):
    """
    Create a new Celery app and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

    celery = Celery(app.import_name)
    celery.conf.update(app.config.get("CELERY_CONFIG", {}))
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    return celery


def create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.

    :param settings_override: Override settings
    :return: Flask app
    """
    app = Flask(__name__, static_folder="../public", static_url_path="")
    app.config.from_object("config.settings")

    if settings_override:
        app.config.update(settings_override)

    middleware(app)

    app.register_blueprint(page)
    app.register_blueprint(products, url_prefix="/api/products")
    app.register_blueprint(
        reservations, url_prefix="/api/products/reservations"
    )

    extensions(app)

    swagger = Swagger(app)

    return app


def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    debug_toolbar.init_app(app)
    db.init_app(app)
    flask_static_digest.init_app(app)

    return None


def middleware(app):
    """
    Register 0 or more middleware (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    # Enable the Flask interactive debugger in the brower for development.
    if app.debug:
        app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

    # Set the real IP address into request.remote_addr when behind a proxy.
    app.wsgi_app = ProxyFix(app.wsgi_app)

    return None


celery_app = create_celery_app()

@celery_app.task
def expireFungibleReservation(id):
    expire_reservation.expire(id, FungibleReservation)

@celery_app.task
def expireNonFungibleReservation(id):
    expire_reservation.expire(id, NonFungibleReservation)
from flask import Blueprint
from http import HTTPStatus

from bitcoinstore.extensions import db
from bitcoinstore.initializers import redis

from .products import products

api = Blueprint("api/v1", __name__)


@api.get("/up")
def up():
    redis.ping()
    db.engine.execute("SELECT 1")
    return ("", HTTPStatus.OK)


api.register_blueprint(products, url_prefix="/products")

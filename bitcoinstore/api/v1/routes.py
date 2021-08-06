from flask import Blueprint, request, make_response, jsonify

from bitcoinstore.extensions import db
from bitcoinstore.initializers import redis
from bitcoinstore.api.v1.product.routes import product

api = Blueprint("api", __name__)
api.register_blueprint(product, url_prefix="/product")


@api.get("/up")
def up():
    redis.ping()
    db.engine.execute("SELECT 1")
    return ""

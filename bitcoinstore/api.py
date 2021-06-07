from flask import Blueprint

from bitcoinstore.extensions import db
from bitcoinstore.initializers import redis

api = Blueprint("api/v1", __name__)


@api.get("/up")
def up():
    redis.ping()
    db.engine.execute("SELECT 1")
    return ""

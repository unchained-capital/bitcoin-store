from http import HTTPStatus

from flask import Blueprint, make_response, jsonify, request

from bitcoinstore.extensions import db
from bitcoinstore.initializers import redis
from bitcoinstore.model.product import NonFungibleProduct, FungibleProduct, Product

products = Blueprint("products", __name__, template_folder="templates")

@products.get("")
def getAll():
    products = (
        db.session.query(Product)
            .all()
    )
    return make_response(jsonify(products), 200)

@products.post("")
def create():
    args = request.json

    if (args.get("qty") is None and args.get("serial") is None) or \
            (args.get("qty") is not None and args.get("serial") is not None):
        return "serial or qty field is required, they are mutually exclusive", 400

    product = Product(
        sku = args.get("sku"),
        name = args.get("name"),
        description = args.get("description"),
        price = args.get("price"),
        weight = args.get("weight"),
    )

    # flush product to autogenerate product.id
    db.session.add(product)
    db.session.flush()

    non_fungible = None
    fungible = None

    # non-fungibles have a unique serial number
    if args.get("serial") is not None:
        non_fungible = NonFungibleProduct(
            productId=product.id,
            serial = args.get("serial"),
            nfpDesc = args.get("nfp_desc"),
        )
    elif args.get("qty") is not None:
        fungible = FungibleProduct(
            productId=product.id,
            qty = args.get("qty"),
            qtyReserved = args.get("qtyReserved") if args.get("qtyReserved") is not None else 0,
        )

    if non_fungible:
        db.session.add(non_fungible)
    else:
        db.session.add(fungible)

    db.session.commit()
    return (jsonify(product), HTTPStatus.CREATED)

@products.get("/up")
def up():
    redis.ping()
    db.engine.execute("SELECT 1")
    return ""

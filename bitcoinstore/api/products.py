from http import HTTPStatus

from flask import Blueprint, jsonify, request, current_app
from sqlalchemy.exc import IntegrityError

from bitcoinstore.extensions import db
from bitcoinstore.initializers import redis
from bitcoinstore.model.product import NonFungibleProduct, FungibleProduct

products = Blueprint("products", __name__, template_folder="templates")

# TODO add query param: sku
# TODO pagination
@products.get("")
def getAll():
    fps = (
        db.session.query(FungibleProduct)
            .all()
    )
    nfps = (
        db.session.query(NonFungibleProduct)
            .all()
    )

    return jsonify(serialize(nfps) + serialize(fps)), HTTPStatus.OK

# TODO add query param: sku
@products.get("fungible")
def getFungibleAll():
    products = (
        db.session.query(FungibleProduct)
            .all()
    )

    return jsonify(serialize(products)), HTTPStatus.OK

@products.get("fungible/<string:id>")
def getFungible(id):
    product = (
        FungibleProduct.query.get(id)
    )

    return jsonify(serialize(product)), HTTPStatus.OK

# TODO add query params: sku, serial
@products.get("nonfungible")
def getNonFungibleAll():
    products = (
        db.session.query(NonFungibleProduct)
            .all()
    )

    return jsonify(serialize(products)), HTTPStatus.OK

@products.get("nonfungible/<string:id>")
def getNonFungible(id):
    products = (
        NonFungibleProduct.query.get(id)
    )

    return jsonify(serialize(products)), HTTPStatus.OK

@products.post("")
def create():
    args = request.json
    if not args:
        return "payload required", HTTPStatus.BAD_REQUEST

    if "fungible" not in args:
        return "fungible is required", HTTPStatus.BAD_REQUEST
    elif args.get("fungible") == False and "serial" not in args:
        return "serial is required for non-fungible products", HTTPStatus.BAD_REQUEST

    if "sku" not in args:
        return "sku is required", HTTPStatus.BAD_REQUEST

    is_fungible = args.get("fungible")

    try:
        if is_fungible:
            product = FungibleProduct(
                sku = args.get("sku"),
                name = args.get("name"),
                description = args.get("description"),
                qty = args.get("qty"),
                qty_reserved = args.get("qty_reserved"),
                price=args.get("price"),
                weight=args.get("weight"),
            )
        else:
            product = NonFungibleProduct(
                sku = args.get("sku"),
                name = args.get("name"),
                description = args.get("description"),
                serial = args.get("serial"),
                nfp_desc = args.get("nfp_desc"),
                reserved = args.get("reserved"),
                price=args.get("price"),
                weight=args.get("weight"),
            )

        db.session.add(product)
        db.session.commit()

    except IntegrityError as ie:
        current_app.logger.info(ie)
        db.session.rollback()
        return ie.orig.diag.message_detail, HTTPStatus.CONFLICT

    return jsonify(product.serialize()), HTTPStatus.CREATED

@products.get("/up")
def up():
    redis.ping()
    db.engine.execute("SELECT 1")
    return ""

def serialize(products):
    if isinstance(products, FungibleProduct):
        return FungibleProduct.serialize(products)
    elif isinstance(products, NonFungibleProduct):
        return NonFungibleProduct.serialize(products)

    serialized = []
    for product in products:
        if isinstance(product, FungibleProduct):
            serialized.append(FungibleProduct.serialize(product))
        elif isinstance(product, NonFungibleProduct):
            serialized.append(NonFungibleProduct.serialize(product))
        else:
            raise Exception("list contains object that is not FungibleProduct or NonFungibleProduct")

    return serialized

from http import HTTPStatus

from flask import Blueprint, jsonify, request, current_app
from sqlalchemy.exc import IntegrityError, DBAPIError

from bitcoinstore.extensions import db
from bitcoinstore.initializers import redis
from bitcoinstore.model.product import NonFungibleProduct, FungibleProduct

products = Blueprint("products", __name__, template_folder="templates")

@products.get("/up")
def up():
    redis.ping()
    db.engine.execute("SELECT 1")
    return ""

# TODO add query param: sku
# TODO pagination
@products.get("")
def getAll():
    fps = db.session.query(FungibleProduct).all()
    nfps = db.session.query(NonFungibleProduct).all()

    return jsonify(serialize(nfps) + serialize(fps)), HTTPStatus.OK

# TODO add query param: sku
@products.get("fungible")
def getFungibleAll():
    return getAllOfType(FungibleProduct)

@products.get("nonfungible")
def getNonFungibleAll():
    return getAllOfType(NonFungibleProduct)

def getAllOfType(type):
    products = db.session.query(type).all()

    return jsonify(serialize(products)), HTTPStatus.OK

# TODO add query params: sku, serial
@products.get("fungible/<string:id>")
def getFungible(id):
    return getProduct(FungibleProduct, id)

@products.get("nonfungible/<string:id>")
def getNonFungible(id):
    return getProduct(NonFungibleProduct, id)

def getProduct(type, id):
    product = type.query.get(id)

    if not product:
        return "Not found: " + type.__name__ + ".id=" + id, HTTPStatus.NOT_FOUND
    return jsonify(serialize(product)), HTTPStatus.OK

# TODO split into fungible and nonfungible URLs, remove fungible param from input
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
    error = commit()
    if error:
        return error

    return jsonify(product.serialize()), HTTPStatus.CREATED

@products.put("nonfungible/<string:id>")
def updateNonFungible(id):
    return updateProduct(NonFungibleProduct, id)

@products.put("fungible/<string:id>")
def updateFungible(id):
    return updateProduct(FungibleProduct, id)

def updateProduct(type, id):
    product = db.session.query(type).get(id)
    if product is None:
        return "Not found: " + type.__name__ + ".id=" + id, HTTPStatus.NOT_FOUND

    args = request.json
    if not args:
        return "payload required", HTTPStatus.BAD_REQUEST

    for key in type.__dict__.keys():
        # can't update id
        if key == 'id':
            continue
        if key in args:
            setattr(product, key, args[key])

    error = commit()
    if error:
        return error

    return jsonify(serialize(product)), HTTPStatus.OK

@products.delete("fungible/<string:id>")
def deleteFungible(id):
    return deleteProduct(FungibleProduct, id)

@products.delete("nonfungible/<string:id>")
def deleteNonFungible(id):
    return deleteProduct(NonFungibleProduct, id)

def deleteProduct(type, id):
    product = type.query.get(id)

    if not product:
        return "Not found: " + type.__name__ + ".id=" + id, HTTPStatus.NOT_FOUND

    db.session.delete(product)
    error = commit()
    if error:
        return error

    return "", HTTPStatus.NO_CONTENT

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

def commit():
    try:
        db.session.commit()
    except IntegrityError as ie:
        current_app.logger.info(ie)
        db.session.rollback()
        return ie.orig.diag.message_detail, HTTPStatus.CONFLICT
    except DBAPIError as dbe:
        current_app.logger.info(dbe)
        db.session.rollback()
        return str(dbe.orig), HTTPStatus.BAD_REQUEST

    # TODO match up other db errors with HTTP codes: HTTP 500 for non-user errors, etc.

    return None
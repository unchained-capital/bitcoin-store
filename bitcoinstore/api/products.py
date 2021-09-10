from http import HTTPStatus

from flask import Blueprint, jsonify, request, current_app
from sqlalchemy.exc import IntegrityError, DBAPIError

from bitcoinstore.extensions import db
from bitcoinstore.model.product import (
    NonFungibleProduct,
    FungibleProduct,
    NonFungibleSku,
)

products = Blueprint("products", __name__, template_folder="templates")

# TODO pagination
@products.get("fungible")
def queryFungible():
    query_params = []
    if request.args.get("sku"):
        query_params.append(FungibleProduct.sku == request.args.get("sku"))

    return query(FungibleProduct, query_params)


# TODO pagination
@products.get("nonfungible")
def queryNonFungible():
    query_params = []
    if request.args.get("sku"):
        query_params.append(NonFungibleProduct.sku == request.args.get("sku"))
    if request.args.get("serial"):
        query_params.append(
            NonFungibleProduct.serial == request.args.get("serial")
        )

    return query(NonFungibleProduct, query_params)


def query(type, query_params):
    products = db.session.query(type).filter(*query_params).all()

    return jsonify(serialize(products)), HTTPStatus.OK


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


@products.post("fungible")
def createFungible():
    args = request.json
    if not args:
        return "payload required", HTTPStatus.BAD_REQUEST

    if "sku" not in args:
        return "sku is required", HTTPStatus.BAD_REQUEST

    product = FungibleProduct(
        sku=args.get("sku"),
        name=args.get("name"),
        description=args.get("description"),
        qty=args.get("qty"),
        qty_reserved=args.get("qty_reserved"),
        price=args.get("price"),
        weight=args.get("weight"),
    )

    db.session.add(product)
    error = commit()
    if error:
        return error

    return jsonify(product.serialize()), HTTPStatus.CREATED


@products.post("nonfungible")
def createNonFungible():
    args = request.json
    if not args:
        return "payload required", HTTPStatus.BAD_REQUEST

    if "serial" not in args:
        return "sku is required", HTTPStatus.BAD_REQUEST

    if "sku" not in args:
        return "sku is required", HTTPStatus.BAD_REQUEST

    # create non fungible sku row if it does not exist
    getOrCreateNonFungibleSku(args)

    product = NonFungibleProduct(
        sku=args.get("sku"),
        serial=args.get("serial"),
        nfp_desc=args.get("nfp_desc"),
        price=args.get("price"),
        weight=args.get("weight"),
    )

    db.session.add(product)
    error = commit()
    if error:
        return error

    return jsonify(product.serialize()), HTTPStatus.CREATED


def getOrCreateNonFungibleSku(args):
    nfs = NonFungibleSku.query.get(args.get("sku"))
    if not nfs:
        nfs = NonFungibleSku(
            sku=args.get("sku"),
            name=args.get("name"),
            description=args.get("description"),
        )
        db.session.add(nfs)

    return nfs


@products.put("nonfungible/<string:id>")
def updateNonFungible(id):
    product = db.session.query(NonFungibleProduct).get(id)
    if product is None:
        return (
            "Not found: " + NonFungibleProduct.__name__ + ".id=" + id,
            HTTPStatus.NOT_FOUND,
        )

    args = request.json
    if not args:
        return "payload required", HTTPStatus.BAD_REQUEST

    getOrCreateNonFungibleSku(args)

    setattr(product, "sku", args["sku"])
    setattr(product, "serial", args["serial"])
    setattr(product, "nfp_desc", args["nfp_desc"])
    setattr(product, "price", args["price"])
    setattr(product, "weight", args["weight"])

    error = commit()
    if error:
        return error

    return jsonify(serialize(product)), HTTPStatus.OK


@products.put("fungible/<string:id>")
def updateFungible(id):
    product = db.session.query(FungibleProduct).get(id)
    if product is None:
        return (
            "Not found: " + FungibleProduct.__name__ + ".id=" + id,
            HTTPStatus.NOT_FOUND,
        )

    args = request.json
    if not args:
        return "payload required", HTTPStatus.BAD_REQUEST

    for key in FungibleProduct.__dict__.keys():
        # can't update id
        if key == "id":
            continue
        if key in args:
            setattr(product, key, args[key])

    error = commit()
    if error:
        return error

    return jsonify(serialize(product)), HTTPStatus.OK


@products.delete("fungible/<string:id>")
def deleteFungible(id):
    return delete(FungibleProduct, id)


@products.delete("nonfungible/<string:id>")
def deleteNonFungible(id):
    return delete(NonFungibleProduct, id)


@products.delete("nonfungiblesku/<string:sku>")
def deleteNonFungibleSku(sku):
    return delete(NonFungibleSku, sku)


def delete(type, id):
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
            raise Exception(
                "list contains object that is not FungibleProduct or NonFungibleProduct"
            )

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

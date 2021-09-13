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
    """Query all fungible products
    ---
    parameters:
      - in: query
        name: sku
        required: false
        description: filter by sku
        type: string
    responses:
      200:
        description: a list of fungible products
        schema:
          id: FungibleProduct
          properties:
            description:
              type: string
            fungible_id:
              type: integer
              readOnly: true
            fungible:
              type: boolean
              default: true
              readOnly: true
            name:
              type: string
            price:
              type: integer
              description: measured in pennies
            qty:
              type: integer
            qty_reserved:
              type: integer
            sku:
              type: string
              description: cannot be updated
            weight:
              type: number
          required:
            - sku
    """
    query_params = []
    if request.args.get("sku"):
        query_params.append(FungibleProduct.sku == request.args.get("sku"))

    return query(FungibleProduct, query_params)


# TODO pagination
@products.get("nonfungible")
def queryNonFungible():
    """Query all non fungible products
    ---
    parameters:
      - in: query
        name: sku
        required: false
        description: filter by sku
        type: string
      - in: query
        name: serial
        required: false
        description: filter by serial
        type: string
    responses:
      200:
        description: a list of non fungible products
        schema:
          id: NonFungibleProduct
          properties:
            description:
              type: string
              description: cannot be updated
            fungible:
              type: boolean
              default: false
              readOnly: true
            name:
              type: string
              description: cannot be updated
            nfp_desc:
              type: string
            non_fungible_id:
              type: integer
              readOnly: true
            price:
              type: integer
              description: measured in pennies
            reserved:
              type: boolean
            serial:
              type: string
              description: unique identifier, cannot be updated
            sku:
              type: string
            weight:
              type: number
          required:
            - sku
            - serial
    """
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
    """Query fungible product by id
    ---
    parameters:
      - in: path
        name: id
        required: true
        description: fungible product ID
        type: integer
    responses:
      200:
        description: fungible product
        schema:
          $ref: '#/definitions/FungibleProduct'
      404:
        description: not found
    """
    return getProduct(FungibleProduct, id)


@products.get("nonfungible/<string:id>")
def getNonFungible(id):
    """Query non fungible product by id
    ---
    parameters:
      - in: path
        name: id
        required: true
        description: non fungible product ID
        type: integer
    responses:
      200:
        description: non fungible product
        schema:
          $ref: '#/definitions/NonFungibleProduct'
      404:
        description: not found
    """
    return getProduct(NonFungibleProduct, id)


def getProduct(type, id):
    product = type.query.get(id)

    if not product:
        return "Not found: " + type.__name__ + ".id=" + id, HTTPStatus.NOT_FOUND
    return jsonify(serialize(product)), HTTPStatus.OK


@products.post("fungible")
def createFungible():
    """Create fungible product
    ---
    parameters:
      - in: body
        name: fungible product
        schema:
          $ref: '#/definitions/FungibleProduct'
    responses:
      201:
        description: created
        schema:
          $ref: '#/definitions/FungibleProduct'
      409:
        description: if sku already exists
      400:
        description: error e.g. integer out of range, missing payload
    """
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
    """Create non fungible product
    ---
    parameters:
      - in: body
        name: non fungible product
        schema:
          $ref: '#/definitions/NonFungibleProduct'
    responses:
      201:
        description: created
        schema:
          $ref: '#/definitions/NonFungibleProduct'
      400:
        description: error e.g. integer out of range, missing payload
      409:
        description: if serial already exists
    """
    args = request.json
    if not args:
        return "payload required", HTTPStatus.BAD_REQUEST

    if "serial" not in args:
        return "serial is required", HTTPStatus.BAD_REQUEST

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
    """Update non fungible product
    ---
    parameters:
      - in: path
        name: id
        required: true
        description: non fungible product ID
        type: integer
      - in: body
        name: non fungible product
        schema:
          $ref: '#/definitions/NonFungibleProduct'
    responses:
      200:
        description: updated
        schema:
          $ref: '#/definitions/NonFungibleProduct'
      400:
        description: error e.g. integer out of range, missing payload
      404:
        description: product not found
    """
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
    """Update fungible product
    ---
    parameters:
      - in: path
        name: id
        required: true
        description: fungible product ID
        type: integer
      - in: body
        name: fungible product
        schema:
          $ref: '#/definitions/FungibleProduct'
    responses:
      200:
        description: updated
        schema:
          $ref: '#/definitions/FungibleProduct'
      400:
        description: error e.g. integer out of range, missing payload
      404:
        description: product not found
    """
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
    """Delete fungible product
    ---
    parameters:
      - in: path
        name: id
        required: true
        description: fungible product ID
        type: integer
    responses:
      204:
        description: deleted
      404:
        description: product not found
      409:
        description: database conflict e.g. item has outstanding reservation
    """
    return delete(FungibleProduct, id)


@products.delete("nonfungible/<string:id>")
def deleteNonFungible(id):
    """Delete non fungible product
    ---
    parameters:
      - in: path
        name: id
        required: true
        description: non fungible product ID
        type: integer
    responses:
      204:
        description: deleted
      404:
        description: product not found
      409:
        description: database conflict e.g. item has outstanding reservation
    """
    return delete(NonFungibleProduct, id)


@products.delete("nonfungiblesku/<string:sku>")
def deleteNonFungibleSku(sku):
    """Delete non fungible sku
    ---
    parameters:
      - in: path
        name: sku
        required: true
        description: non fungible product sku
        type: string
    responses:
      204:
        description: deleted
      404:
        description: sku not found
      409:
        description: database conflict e.g. item has outstanding reservation
    """
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

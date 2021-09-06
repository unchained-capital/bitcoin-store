from http import HTTPStatus

from flask import Blueprint, jsonify, request, current_app
from sqlalchemy.exc import IntegrityError

from bitcoinstore.extensions import db
from bitcoinstore.initializers import redis
from bitcoinstore.model.product import NonFungibleProduct, FungibleProduct, Product

products = Blueprint("products", __name__, template_folder="templates")

fungible_fields = {"qty","qty_reserved"}
non_fungible_fields = {"serial","nfp_desc","reserved"}

@products.get("")
def getAll():
    products = (
        db.session.query(Product)
            .all()
    )

    return jsonify([Product.serialize(product) for product in products]), HTTPStatus.OK

@products.post("")
def create():
    args = request.json
    if not args:
        return "payload required", HTTPStatus.BAD_REQUEST

    if "fungible" not in args:
        return "fungible is required", HTTPStatus.BAD_REQUEST
    elif not args.get("fungible") and "serial" not in args:
        return "serial is required for non-fungible products", HTTPStatus.BAD_REQUEST

    is_fungible = args.get("fungible")

    # if they specify fungible=true and non fungible fields or vice versa, kick them out with an error
    if (args.get("fungible") and non_fungible_fields.intersection(set(args.keys()))) or \
            (not args.get("fungible") and fungible_fields.intersection(set(args.keys()))):
        return "fungible="+str(args.get("fungible"))+" but payload includes invalid fields. fungible_fields="+ \
               str(fungible_fields) + " non_fungible_fields=" + str(non_fungible_fields), HTTPStatus.BAD_REQUEST

    product = Product(
        sku = args.get("sku"),
        name = args.get("name"),
        description = args.get("description"),
        price = args.get("price"),
        weight = args.get("weight"),
    )

    try:
        db.session.add(product)
        # write product to db session to autogenerate product.id
        db.session.flush()

        if is_fungible:
            fungible = FungibleProduct(
                productId=product.id,
                qty = args.get("qty"),
                qty_reserved = args.get("qty_reserved"),
            )
            db.session.add(fungible)
        else:
            non_fungible = NonFungibleProduct(
                productId=product.id,
                serial = args.get("serial"),
                nfp_desc = args.get("nfp_desc"),
            )
            db.session.add(non_fungible)

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

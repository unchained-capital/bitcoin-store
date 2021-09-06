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
    # this only breaks in test
    # db.session.autoflush=False

    fps = (
        db.session.query(FungibleProduct)
            .all()
    )
    nfps = (
        db.session.query(NonFungibleProduct)
            .all()
    )

    return jsonify({
        "fungible_products":[FungibleProduct.serialize(fp) for fp in fps],
        "non_fungible_products":[NonFungibleProduct.serialize(nfp) for nfp in nfps]
    }), HTTPStatus.OK

@products.get("/<string:sku>")
def get(sku):
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

    if "sku" not in args:
        return "sku is required", HTTPStatus.BAD_REQUEST

    is_fungible = args.get("fungible")

    # if they specify fungible=true and non fungible fields or vice versa, kick them out with an error
    if (args.get("fungible") and non_fungible_fields.intersection(set(args.keys()))) or \
            (not args.get("fungible") and fungible_fields.intersection(set(args.keys()))):
        return "fungible="+str(args.get("fungible"))+" but payload includes invalid fields. fungible_fields="+ \
               str(fungible_fields) + " non_fungible_fields=" + str(non_fungible_fields), HTTPStatus.BAD_REQUEST

    sku=args.get("sku"),
    name=args.get("name"),
    description=args.get("description")

    try:
        # Note: we do not update existing product fields. If the caller
        # passes in different product name or desc we can ignore it or
        # throw an error. Let's ignore it for now
        product = Product.query.filter_by(
            sku=args.get("sku")
        ).first()

        if product is None:
            product = Product(sku=sku, name=name, description=description)

            # write product to db to update fields or autogenerate product.id
            db.session.add(product)
            db.session.flush()

        if is_fungible:
            fungible = FungibleProduct(
                productId=product.id,
                # product=product,
                qty = args.get("qty"),
                qty_reserved = args.get("qty_reserved"),
                price=args.get("price"),
                weight=args.get("weight"),
            )
            db.session.add(fungible)
            db.session.commit()
            product.fungible = fungible
            product.nonFungible = None
        else:
            non_fungible = NonFungibleProduct(
                productId=product.id,
                # product=product,
                serial = args.get("serial"),
                nfp_desc = args.get("nfp_desc"),
                price=args.get("price"),
                weight=args.get("weight"),
            )
            db.session.add(non_fungible)
            db.session.commit()
            product.nonFungible = non_fungible
            product.fungible = None

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

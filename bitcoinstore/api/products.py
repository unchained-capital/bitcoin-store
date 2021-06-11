from decimal import Decimal
from flask import Blueprint, current_app, jsonify, request, url_for
from http import HTTPStatus
from sqlalchemy.exc import SQLAlchemyError

from bitcoinstore.extensions import db
from bitcoinstore.models.product import Product

products = Blueprint("products", __name__)


@products.post("/")
def create():
    """Create a Product

    Accepts the following parameters:
    * sku (string) - stock keeping unit
    * name (string) - short name
    * description (string) - long description
    * color (string)
    * unit_price_subunits (integer) - price denominated in subunits of the
        relevant currency, e.g. in cents for USD or in sats for BTC
    * unit_price_currency (string) - the native currency for the price, denoted
        in three-letter ISO 4217 currency codes for fiat, or 'BTC' for Bitcoin.
        Defaults to 'USD'.
    * shipping_weight_kg (decimal) - the shipping weight of the product in KG,
        or decimal amounts thereof.

    On success, returns HTTP Created response, with the product's URL in the
    Location response header.
    """
    args = request.args

    product = Product(
        sku=args.get("sku"),
        name=args.get("name"),
        description=args.get("description"),
        color=args.get("color"),
        unit_price_subunits=args.get("unit_price_subunits", type=int),
        unit_price_currency=args.get("unit_price_currency", default="USD"),
        shipping_weight_kg=args.get("shipping_weight_kg", type=Decimal),
    )

    try:
        db.session.add(product)
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        return (repr(e), HTTPStatus.UNPROCESSABLE_ENTITY)

    return (
        jsonify(id=product.id),
        HTTPStatus.CREATED,
        {"Location": url_for("api/v1.products.update", id=product.id)},
    )


@products.patch("/<int:id>")
def update(id):
    """Update a product, by id

    Accepts the following parameters, and updates the product field if the
    value is not blank:
    * name (string) - short name
    * description (string) - long description
    * color (string)
    * unit_price_subunits (integer) - price denominated in subunits of the
        relevant currency, e.g. in cents for USD or in sats for BTC
    * unit_price_currency (string) - the native currency for the price, denoted
        in three-letter ISO 4217 currency codes for fiat, or 'BTC' for Bitcoin.
        Defaults to 'USD'.
    * shipping_weight_kg (decimal) - the shipping weight of the product in KG,
        or decimal amounts thereof.

    On success, returns HTTP OK response.
    """
    args = request.args

    product = Product.query.get_or_404(id)

    if args.get("sku"):
        product.sku = args.get("sku")
    if args.get("name"):
        product.name = args.get("name")
    if args.get("description"):
        product.description = args.get("description")
    if args.get("color"):
        product.color = args.get("color")
    if args.get("unit_price_subunits"):
        product.unit_price_subunits = args.get("unit_price_subunits", type=int)
    if args.get("unit_price_currency"):
        product.unit_price_currency = args.get(
            "unit_price_currency", default="USD"
        )
    if args.get("shipping_weight_kg"):
        product.shipping_weight_kg = args.get(
            "shipping_weight_kg", type=Decimal
        )

    try:
        db.session.add(product)
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        return (repr(e), HTTPStatus.UNPROCESSABLE_ENTITY)

    return ("", HTTPStatus.OK)

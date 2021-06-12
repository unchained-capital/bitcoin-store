from decimal import Decimal
from http import HTTPStatus
from flask import Blueprint, current_app, g, jsonify, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from bitcoinstore.extensions import db
from bitcoinstore.models.product_item import ProductItem

from .reservations import reservations

items = Blueprint("items", __name__)
items.register_blueprint(
    reservations, url_prefix="/<int:product_item_id>/reservations"
)


@items.url_value_preprocessor
def get_product_id(endpoint, values):
    g.product_id = values.pop("product_id")


@items.post("/")
def create():
    """Create a Product Items

    Accepts the following parameters:
    * serial_num (string) - serial number, must be unique for this product
    * description (string) - long description
    * color (string)
    * unit_price_subunits (integer) - price denominated in subunits of the
        relevant currency, e.g. in cents for USD or in sats for BTC
    * unit_price_currency (string) - the native currency for the price, denoted
        in three-letter ISO 4217 currency codes for fiat, or 'BTC' for Bitcoin.
        Defaults to 'USD'.
    * shipping_weight_kg (decimal) - the shipping weight of the product in KG,
        or decimal amounts thereof.
    * amount_in_stock (integer) - the number of available units in stock

    On success, returns HTTP Created response, with the product's URL in the
    Location response header.
    """
    args = request.args

    product_item = ProductItem(
        product_id=g.product_id,
        serial_num=args.get("serial_num"),
        description=args.get("description"),
        color=args.get("color"),
        unit_price_subunits=args.get("unit_price_subunits", type=int),
        unit_price_currency=args.get("unit_price_currency", default="USD"),
        shipping_weight_kg=args.get("shipping_weight_kg", type=Decimal),
        amount_in_stock=args.get("amount_in_stock", type=int),
    )

    try:
        db.session.add(product_item)
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        return (repr(e), HTTPStatus.UNPROCESSABLE_ENTITY)

    return (
        jsonify(id=product_item.id),
        HTTPStatus.CREATED,
        {
            "Location": url_for(
                "api/v1.products.items.update",
                product_id=g.product_id,
                id=product_item.id,
            )
        },
    )


@items.patch("/<int:id>")
def update(id):
    """Update a product item, by id

    Accepts the following parameters, and updates the product field if the
    value is not blank:
    * serial_num (string) - serial number, must be unique for this product
    * description (string) - long description
    * color (string)
    * unit_price_subunits (integer) - price denominated in subunits of the
        relevant currency, e.g. in cents for USD or in sats for BTC
    * unit_price_currency (string) - the native currency for the price, denoted
        in three-letter ISO 4217 currency codes for fiat, or 'BTC' for Bitcoin.
        Defaults to 'USD'.
    * shipping_weight_kg (decimal) - the shipping weight of the product in KG,
        or decimal amounts thereof.
    * amount_in_stock (integer) - the number of available units in stock

    On success, returns HTTP OK response.
    """
    args = request.args

    product_item = ProductItem.query.filter_by(
        product_id=g.product_id, id=id
    ).first_or_404()

    if args.get("serial_num"):
        product_item.serial_num = args.get("serial_num")
    if args.get("description"):
        product_item.description = args.get("description")
    if args.get("color"):
        product_item.color = args.get("color")
    if args.get("unit_price_subunits"):
        product_item.unit_price_subunits = args.get(
            "unit_price_subunits", type=int
        )
    if args.get("unit_price_currency"):
        product_item.unit_price_currency = args.get(
            "unit_price_currency", default="USD"
        )
    if args.get("shipping_weight_kg"):
        product_item.shipping_weight_kg = args.get(
            "shipping_weight_kg", type=Decimal
        )
    if args.get("amount_in_stock"):
        product_item.amount_in_stock = args.get("amount_in_stock", type=int)

    try:
        db.session.add(product_item)
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        return (repr(e), HTTPStatus.UNPROCESSABLE_ENTITY)

    return ("", HTTPStatus.OK)

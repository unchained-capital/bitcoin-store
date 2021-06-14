from http import HTTPStatus
from flask import Blueprint, current_app, g, jsonify, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from bitcoinstore.extensions import db
from bitcoinstore.models.product_item import ProductItem
from bitcoinstore.models.reservation import Reservation

reservations = Blueprint("reservations", __name__)


@reservations.url_value_preprocessor
def get_product_item_id(endpoint, values):
    # note product_id is loaded up the chain, in the ProductItem
    # url_value_preprocessor
    g.product_item_id = values.pop("product_item_id")


@reservations.post("/")
def create():
    """Create a Reservation for a ProductItem

    For example, when an item is added to a cart, it is reserved for the
    current user.

    Accepts the following parameters:
    * cart_id (integer) - cart for whom this item is being reserved
    * amount (integer, default=1) - number of items to be reserved

    On success, returns HTTP Created (201) response, with the product's URL in
    the Location response header.
    On too few items being available, returns Request Entity Too Large (413)
    """
    args = request.args

    product_item = (
        ProductItem.query.filter_by(
            product_id=g.product_id, id=g.product_item_id
        )
        .with_for_update(nowait=True)
        .first_or_404()
    )

    # TODO: in a reasonable implementation, this endpoint would check
    # for authorization to create a reservation for the given cart.
    reservation = Reservation(
        product_item_id=g.product_item_id,
        cart_id=args.get("cart_id"),
        amount=args.get("amount", type=int, default=1),
    )

    new_amount_reserved = product_item.amount_reserved + reservation.amount
    if new_amount_reserved > product_item.amount_in_stock:
        # Note, this response is a bit of a hack, probably a mis-use of http
        # response codes.
        return (
            jsonify({"amount_in_stock": product_item.amount_in_stock}),
            HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
        )

    product_item.amount_reserved = new_amount_reserved
    try:
        db.session.add(product_item)
        db.session.add(reservation)
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        return (repr(e), HTTPStatus.UNPROCESSABLE_ENTITY)

    return (
        jsonify(id=reservation.id),
        HTTPStatus.CREATED,
        {
            "Location": url_for(
                "api/v1.products.items.reservations.destroy",
                product_id=g.product_id,
                product_item_id=g.product_item_id,
                id=reservation.id,
            )
        },
    )


@reservations.delete("/<int:id>")
def destroy(id):
    """Cancel a reservation

    Removes the reservation and frees the item to be reserved by others.

    On success, returns HTTP OK response.
    """
    product_item = (
        ProductItem.query.filter_by(
            product_id=g.product_id, id=g.product_item_id
        )
        .with_for_update(nowait=True)
        .first_or_404()
    )

    # TODO: in a reasonable implementation, this endpoint would check the
    # caller for authorization to destroy this reservation.
    reservation = Reservation.query.filter_by(
        product_item_id=g.product_item_id, id=id
    ).first_or_404()

    product_item.amount_reserved -= reservation.amount
    try:
        db.session.add(product_item)
        db.session.delete(reservation)
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        return (repr(e), HTTPStatus.UNPROCESSABLE_ENTITY)

    return ("", HTTPStatus.OK)

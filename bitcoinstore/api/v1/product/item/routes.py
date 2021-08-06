from flask import Blueprint, g, request, make_response, jsonify

from bitcoinstore.extensions import db
from bitcoinstore.models.inventory import ProductItem


item = Blueprint("item", __name__)


@item.url_value_preprocessor
def pull_product_id(endpoint, values):
    g.product_id = values.pop("product_id")


@item.route("/", methods=["GET"])
def list():
    product_item = (
        db.session.query(ProductItem)
        .filter(ProductItem.product_id == g.product_id)
        .all()
    )
    return make_response(jsonify(product_item), 200)


@item.route("/", methods=["POST"])
def create():
    if not request.is_json:
        return "Item must be json.", 400

    create_data = request.json

    item_product_id = create_data.get("product_id")
    item_product_id = item_product_id if item_product_id else g.product_id
    if g.product_id != item_product_id:
        return "Product ID URL Param different from item product_id", 400

    color = create_data.get("color")
    serial_number = create_data.get("serial_number")
    notes = create_data.get("notes")
    price = create_data.get("price")
    currency = create_data.get("currency")
    is_reserved = create_data.get("is_reserved")

    product_item = ProductItem(
        product_id=item_product_id,
        color=color,
        serial_number=serial_number,
        notes=notes,
        price=price,
        currency=currency,
        is_reserved=is_reserved,
    )
    db.session.add(product_item)
    db.session.commit()
    return make_response(jsonify(product_item), 201)


@item.route("/<int:id>", methods=["PUT"])
def update(id):
    data = ProductItem.query.get_or_404(id)
    if not request.is_json:
        return "Item must be json.", 400

    update_data = request.get_json()

    data.product_id = data.product_id if data.product_id else g.product_id
    data.color = update_data.get("color")
    data.serial_number = update_data.get("serial_number")
    data.notes = update_data.get("notes")
    data.price = update_data.get("price")
    data.currency = update_data.get("currency")
    data.is_reserved = update_data.get("is_reserved")

    db.session.commit()

    return make_response(jsonify(data), 200)


@item.route("/<int:id>", methods=["GET"])
def read(id):
    data = ProductItem.query.get_or_404(id)
    return make_response(jsonify(data), 200)


@item.route("/<int:id>", methods=["DELETE"])
def delete(id):
    data = ProductItem.query.get_or_404(id)

    db.session.delete(data)
    db.session.commit()

    return make_response(jsonify(data), 200)

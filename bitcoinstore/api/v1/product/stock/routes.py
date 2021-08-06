from flask import Blueprint, g, request, make_response, jsonify

from bitcoinstore.extensions import db
from bitcoinstore.models.inventory import ProductStock


stock = Blueprint("stock", __name__)


@stock.url_value_preprocessor
def pull_product_id(endpoint, values):
    g.product_id = values.pop("product_id")


@stock.route("/", methods=["GET"])
def read_by_product_id():
    product_stock = (
        db.session.query(ProductStock)
        .filter(ProductStock.product_id == g.product_id)
        .first_or_404()
    )
    return make_response(jsonify(product_stock), 200)


@stock.route("/", methods=["POST"])
def create():
    if not request.is_json:
        return "Stock must be json.", 400

    create_data = request.json

    stock_product_id = create_data.get("product_id")
    stock_product_id = stock_product_id if stock_product_id else g.product_id
    if g.product_id != stock_product_id:
        return "Product ID URL Param different from stock product_id", 400

    color = create_data.get("color")
    price = create_data.get("price")
    currency = create_data.get("currency")
    quantity = create_data.get("quantity")
    reserved = create_data.get("reserved")

    product_stock = ProductStock(
        product_id=stock_product_id,
        color=color,
        price=price,
        currency=currency,
        quantity=quantity,
        reserved=reserved,
    )
    db.session.add(product_stock)
    db.session.commit()
    return make_response(jsonify(product_stock), 201)


@stock.route("/<int:id>", methods=["PUT"])
def update(id):
    data = ProductStock.query.get_or_404(id)
    if not request.is_json:
        return "Stock must be json.", 400

    update_data = request.get_json()

    data.product_id = data.product_id if data.product_id else g.product_id
    data.color = update_data.get("color")
    data.price = update_data.get("price")
    data.currency = update_data.get("currency")
    data.quantity = update_data.get("quantity")
    data.reserved = update_data.get("reserved")

    db.session.commit()

    return make_response(jsonify(data), 200)


@stock.route("/<int:id>", methods=["GET"])
def read(id):
    data = ProductStock.query.get_or_404(id)
    return make_response(jsonify(data), 200)


@stock.route("/<int:id>", methods=["DELETE"])
def delete(id):
    data = ProductStock.query.get_or_404(id)

    db.session.delete(data)
    db.session.commit()

    return make_response(jsonify(data), 200)

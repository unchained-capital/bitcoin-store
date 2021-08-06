from flask import Blueprint, request, make_response, jsonify

from bitcoinstore.extensions import db
from bitcoinstore.models.inventory import Product
from bitcoinstore.api.v1.product.stock.routes import stock


product = Blueprint("product", __name__)
product.register_blueprint(stock, url_prefix="/<int:product_id>/stock")


@product.route("/", methods=["GET"])
def list():
    return make_response(jsonify(Product.query.all()), 200)


@product.route("/", methods=["POST"])
def create():
    if not request.is_json:
        return "Product must be json.", 400
    create_data = request.json
    sku = create_data.get("sku")
    if sku == "":
        return "SKU required.", 400
    name = create_data.get("name")
    if name == "":
        return "Name required.", 400
    description = create_data.get("description")
    weight = create_data.get("weight")
    product = Product(
        sku=sku, name=name, description=description, weight=weight
    )
    db.session.add(product)
    db.session.commit()
    return make_response(jsonify(product), 201)


@product.route("/<int:id>", methods=["GET"])
def read(id):
    data = Product.query.get_or_404(id)
    return make_response(jsonify(data), 200)


@product.route("/<int:id>", methods=["PUT"])
def update(id):
    data = Product.query.get_or_404(id)
    if not request.is_json:
        return "Product must be json.", 400

    update_data = request.get_json()

    data.sku = update_data.get("sku")
    data.name = update_data.get("name")
    data.description = update_data.get("description")
    data.weight = update_data.get("weight")

    db.session.commit()

    return make_response(jsonify(data), 200)


@product.route("/<int:id>", methods=["DELETE"])
def delete(id):
    data = Product.query.get_or_404(id)

    db.session.delete(data)
    db.session.commit()

    return make_response(jsonify(data), 200)

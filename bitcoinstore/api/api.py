from flask import Blueprint, request
from bitcoinstore.api.handlers.get_fungible \
    import get_fungible as get_fungible_handler
from bitcoinstore.api.handlers.get_non_fungible \
    import get_non_fungible as get_non_fungible_handler
from bitcoinstore.api.handlers.post_fungible \
    import post_fungible as post_fungible_handler
from bitcoinstore.api.handlers.post_fungible_add_remove \
    import post_fungible_add_remove as post_fungible_add_remove_handler
from bitcoinstore.api.handlers.put_fungible \
    import put_fungible as put_fungible_handler
from bitcoinstore.api.handlers.put_non_fungible \
    import put_non_fungible as put_non_fungible_handler


api = Blueprint("api", __name__)


"""
get_fungible()
Used for retriving fungible items by sku.
"""
@api.get("/api/fungible/<string:sku>")
def get_fungible(sku):
    try:
        return get_fungible_handler(sku)
    except Exception as e:
        print(e)
        return "Internal server error", 500


"""
get_non_fungible()
Used for retriving non-fungible items by sku and sn.
"""
@api.get("/api/non-fungible/<string:sku>/<string:sn>")
def get_non_fungible(sku, sn):
    try:
        return get_non_fungible_handler(sku, sn)
    except Exception as e:
        print(e)
        return "Internal server error", 500


"""
post_fungible()
Used for adding fungible items without a sku.
This creates an item sku.
<body application/json> {
    amount_in_stock: int | undefined
    color: str | undefined
    description: str | undefined
    shipping_weight_grams: int | undefined
    unit_price_cents: int | undefined
}
"""
@api.post("/api/fungible")
def post_fungible():
    try:
        properties = request.json
        return post_fungible_handler(properties)
    except Exception as e:
        print(e)
        return "Internal server error", 500

"""
post_fungible_add()
Used for adding quantity to an item by sku.
"""
@api.post("/api/fungible/<string:sku>/add/<int:quantity>")
def post_fungible_add(sku, quantity):
    try:
        return post_fungible_add_remove_handler(sku, quantity)
    except Exception as e:
        print(e)
        return "Internal server error", 500


"""
post_fungible_remove()
Used for removing quantity from an item by sku.
"""
@api.post("/api/fungible/<string:sku>/remove/<int:quantity>")
def post_fungible_remove(sku, quantity):
    try:
        return post_fungible_add_remove_handler(sku, -quantity)
    except Exception as e:
        print(e)
        return "Internal server error", 500


"""
put_fungible(sku)
Used for adding or updating fungible items by their sku.
If the sku exists, the item is updated else it is added.
<body application/json> {
    amount_in_stock: int | undefined
    color: str | undefined
    description: str | undefined
    shipping_weight_grams: int | undefined
    unit_price_cents: int | undefined
}
"""
@api.put("/api/fungible/<string:sku>")
def put_fungible(sku) -> dict:
    try:
        properties = request.json
        return put_fungible_handler(sku, properties)
    except Exception as e:
        print(e)
        return "Internal server error", 500


"""
put_non_fungible(sn)
Used for adding or updating non-fungible items by their serial number and sku.
If the serial number and sku exists, the item is updated else it is added.
<body application/json> {
    color: str | undefined
    description: str | undefined
    notes: str | undefined
    price_cents: int | undefined
    shipping_weight_grams: int | undefined
    sold: bool | undefined
}
"""
@api.put("/api/non-fungible/<string:sku>/<string:sn>")
def put_non_fungible(sku, sn):
    try:
        properties = request.json
        return put_non_fungible_handler(sku, sn, properties)
    except Exception as e:
        print(e)
        return "Internal server error", 500

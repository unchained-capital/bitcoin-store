from flask import url_for


def create_product(client):
    """
    Create a product for our test session.

    :return: Product json
    """
    json = {
        "sku": "12341234",
        "name": "Wooden Pencil",
        "description": "Yellow, #2, Pre-Sharpened, 30-pack",
        "weight": 0.1,
    }
    response = client.post(url_for("api.product.create"), json=json)
    return response.json


def create_product_stock(client):
    """
    Create a product stock for our test session.

    :return: ProductStock json
    """
    product = create_product(client)
    json = {
        "color": "Yellow",
        "price": 3.0,
        "currency": "USD",
        "quantity": 973,
        "reserved": 0,
    }
    response = client.post(
        url_for("api.product.stock.create", product_id=product["id"]), json=json
    )
    return response.json


def create_product_item(client):
    """
    Create a product item for our test session.

    :return: ProductItem json
    """
    product = create_product(client)
    json = {
        "color": "Yellow",
        "serial_number": "VIN1234134134",
        "notes": "Stratches on the clearcoat on the fuel tank.",
        "price": 3200,
        "currency": "USD",
        "reserved": False,
    }
    response = client.post(
        url_for("api.product.item.create", product_id=product["id"]), json=json
    )
    return response.json

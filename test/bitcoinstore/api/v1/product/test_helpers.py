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

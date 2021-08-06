import test.bitcoinstore.api.v1.product.test_helpers as product_helpers
from flask import url_for
from lib.test import ViewTestMixin


class TestApiV1(ViewTestMixin):
    def test_home_route(self):
        """
        Product api should respond with empty array if there
        are no Products loaded yet, depends on DB init to empty.
        """
        response = self.client.get(url_for("api.product.list"))

        assert response.is_json
        assert response.json == []
        assert response.status_code == 200

    def test_home_route_seeded(self):
        """
        Product api should respond with an array of one Product.
        """
        product = product_helpers.create_product(self.client)
        response = self.client.get(url_for("api.product.list"))

        assert response.is_json
        assert response.json == [product]
        assert response.status_code == 200

    def test_product_route_post_no_data(self):
        """
        Product create api post should respond with a failure 400 on not input.
        """
        response = self.client.post(url_for("api.product.create"))

        assert response.status_code == 400

    def test_product_route_post(self):
        """
        Product api should return product object with an id.
        """
        product = {
            "sku": "12341234",
            "name": "Wooden Pencil",
            "description": "Yellow, #2, Pre-Sharpened, 30-pack",
            "weight": 0.1,
        }
        response = self.client.post(url_for("api.product.create"), json=product)

        assert response.status_code == 201
        assert response.json["sku"] == product["sku"]
        assert response.json["name"] == product["name"]
        assert response.json["description"] == product["description"]
        assert response.json["weight"] == product["weight"]

    def test_product_route_get(self):
        """
        Product read API should return the fully populated Product object.
        """
        product = product_helpers.create_product(self.client)

        response = self.client.get(
            url_for("api.product.read", id=product["id"])
        )

        assert response.status_code == 200
        assert response.json["id"] == product["id"]
        assert response.json["sku"] == product["sku"]
        assert response.json["name"] == product["name"]
        assert response.json["description"] == product["description"]
        assert response.json["weight"] == product["weight"]

    def test_product_route_put(self):
        """
        Product update API should return the updated Product object.
        """
        product = product_helpers.create_product(self.client)

        product["sku"] = "43214321"
        product["name"] = "Metal Pencil"
        product["description"] = "Green, #3, Not-Sharpened, 5-pack"
        product["weight"] = 0.2
        response = self.client.put(
            url_for("api.product.update", id=product["id"]), json=product
        )

        assert response.status_code == 200
        assert response.json["id"] == product["id"]
        assert response.json["sku"] == product["sku"]
        assert response.json["name"] == product["name"]
        assert response.json["description"] == product["description"]
        assert response.json["weight"] == product["weight"]

    def test_product_route_delete(self):
        """
        Product delete API should return the deleted Product object.
        """
        product = product_helpers.create_product(self.client)

        response = self.client.delete(
            url_for("api.product.delete", id=product["id"])
        )
        assert response.status_code == 200
        assert response.json["id"] == product["id"]
        assert response.json["sku"] == product["sku"]
        assert response.json["name"] == product["name"]
        assert response.json["description"] == product["description"]
        assert response.json["weight"] == product["weight"]

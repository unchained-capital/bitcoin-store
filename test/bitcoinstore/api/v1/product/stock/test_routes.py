import test.bitcoinstore.api.v1.product.test_helpers as product_helpers
from flask import url_for
from lib.test import ViewTestMixin


class TestApiV1(ViewTestMixin):
    def test_home_route(self):
        """
        Stock api should respond with 404 if there
        are no Stock for the product.
        """
        product = product_helpers.create_product(self.client)
        response = self.client.get(
            url_for(
                "api.product.stock.read_by_product_id", product_id=product["id"]
            )
        )

        assert response.status_code == 404

    def test_home_route_seeded(self):
        """
        Stock api should respond with one Stock object.
        """
        stock = product_helpers.create_product_stock(self.client)
        response = self.client.get(
            url_for(
                "api.product.stock.read_by_product_id",
                product_id=stock["product_id"],
            )
        )

        assert response.is_json
        assert response.json == stock
        assert response.status_code == 200

    def test_stock_route_post_no_data(self):
        """
        Stock create api post should respond with a failure 400 on not input.
        """
        product = product_helpers.create_product(self.client)

        response = self.client.post(
            url_for("api.product.stock.create", product_id=product["id"])
        )

        assert response.status_code == 400

    def test_stock_route_post(self):
        """
        Stock api should return product stock object with an id.
        """
        product = product_helpers.create_product(self.client)

        stock = {
            "product_id": product["id"],
            "color": "Yellow",
            "price": 3.0,
            "currency": "USD",
            "quantity": 973,
            "reserved": 0,
        }
        response = self.client.post(
            url_for("api.product.stock.create", product_id=product["id"]),
            json=stock,
        )

        assert response.status_code == 201
        assert response.json["product_id"] == stock["product_id"]
        assert response.json["color"] == stock["color"]
        assert response.json["price"] == stock["price"]
        assert response.json["currency"] == stock["currency"]
        assert response.json["quantity"] == stock["quantity"]
        assert response.json["reserved"] == stock["reserved"]

    def test_stock_route_get(self):
        """
        Stock read API should return the fully popluated Stock object.
        """
        stock = product_helpers.create_product_stock(self.client)

        response = self.client.get(
            url_for(
                "api.product.stock.read",
                product_id=stock["product_id"],
                id=stock["id"],
            )
        )

        assert response.status_code == 200
        assert response.json["product_id"] == stock["product_id"]
        assert response.json["color"] == stock["color"]
        assert response.json["price"] == stock["price"]
        assert response.json["currency"] == stock["currency"]
        assert response.json["quantity"] == stock["quantity"]
        assert response.json["reserved"] == stock["reserved"]

    def test_stock_route_put(self):
        """
        Stock update API should return the updated Stock object.
        """
        stock = product_helpers.create_product_stock(self.client)

        stock["color"] = "Blue"
        stock["price"] = 32.5
        stock["currency"] = "USD"
        stock["quantity"] = 42
        stock["reserved"] = 5
        response = self.client.put(
            url_for(
                "api.product.stock.update",
                product_id=stock["product_id"],
                id=stock["id"],
            ),
            json=stock,
        )

        assert response.status_code == 200
        assert response.json["product_id"] == stock["product_id"]
        assert response.json["color"] == stock["color"]
        assert response.json["price"] == stock["price"]
        assert response.json["currency"] == stock["currency"]
        assert response.json["quantity"] == stock["quantity"]
        assert response.json["reserved"] == stock["reserved"]

    def test_stock_route_delete(self):
        """
        Stock update API should return the deleted Stock object.
        """
        stock = product_helpers.create_product_stock(self.client)

        response = self.client.delete(
            url_for(
                "api.product.stock.delete",
                product_id=stock["product_id"],
                id=stock["id"],
            )
        )
        assert response.status_code == 200
        assert response.json["product_id"] == stock["product_id"]
        assert response.json["color"] == stock["color"]
        assert response.json["price"] == stock["price"]
        assert response.json["currency"] == stock["currency"]
        assert response.json["quantity"] == stock["quantity"]
        assert response.json["reserved"] == stock["reserved"]

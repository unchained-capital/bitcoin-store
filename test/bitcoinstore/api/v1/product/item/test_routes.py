import test.bitcoinstore.api.v1.product.test_helpers as product_helpers
from flask import url_for
from lib.test import ViewTestMixin


class TestApiV1(ViewTestMixin):
    def test_home_route(self):
        """
        Item api should respond with empty array if there
        are no items for the product.
        """
        product = product_helpers.create_product(self.client)
        response = self.client.get(
            url_for("api.product.item.list", product_id=product["id"])
        )

        assert response.status_code == 200

    def test_home_route_seeded(self):
        """
        Item api should respond with one Item object in list.
        """
        item = product_helpers.create_product_item(self.client)
        response = self.client.get(
            url_for(
                "api.product.item.list",
                product_id=item["product_id"],
            )
        )

        assert response.is_json
        assert response.json == [item]
        assert response.status_code == 200

    def test_item_route_post_no_data(self):
        """
        Item create api post should respond with a failure 400 on not input.
        """
        product = product_helpers.create_product(self.client)

        response = self.client.post(
            url_for("api.product.item.create", product_id=product["id"])
        )

        assert response.status_code == 400

    def test_item_route_post(self):
        """
        Item api should return product stock object with an id.
        """
        product = product_helpers.create_product(self.client)

        data = {
            "product_id": product["id"],
            "color": "Yellow",
            "serial_number": "VIN1234134134",
            "notes": "Stratches on the clearcoat on the fuel tank.",
            "price": 3200,
            "currency": "USD",
            "is_reserved": False,
        }
        response = self.client.post(
            url_for("api.product.item.create", product_id=product["id"]),
            json=data,
        )

        assert response.status_code == 201
        assert response.json["product_id"] == data["product_id"]
        assert response.json["color"] == data["color"]
        assert response.json["serial_number"] == data["serial_number"]
        assert response.json["notes"] == data["notes"]
        assert response.json["price"] == data["price"]
        assert response.json["currency"] == data["currency"]
        assert response.json["is_reserved"] == data["is_reserved"]

    def test_item_route_get(self):
        """
        Item read API should return the fully populated Item object.
        """
        data = product_helpers.create_product_item(self.client)

        response = self.client.get(
            url_for(
                "api.product.item.read",
                product_id=data["product_id"],
                id=data["id"],
            )
        )

        assert response.status_code == 200
        assert response.json["product_id"] == data["product_id"]
        assert response.json["color"] == data["color"]
        assert response.json["serial_number"] == data["serial_number"]
        assert response.json["notes"] == data["notes"]
        assert response.json["price"] == data["price"]
        assert response.json["currency"] == data["currency"]
        assert response.json["is_reserved"] == data["is_reserved"]

    def test_item_route_put(self):
        """
        Item update API should return the updated Item object.
        """
        data = product_helpers.create_product_item(self.client)

        data["color"] = "Blue"
        data["serial_number"] = "VIN1ASDF56789"
        data["notes"] = "No major dings, dents, or stratches."
        data["price"] = 3250
        data["currency"] = "USD"
        data["reserved"] = True
        response = self.client.put(
            url_for(
                "api.product.item.update",
                product_id=data["product_id"],
                id=data["id"],
            ),
            json=data,
        )

        assert response.status_code == 200
        assert response.json["product_id"] == data["product_id"]
        assert response.json["color"] == data["color"]
        assert response.json["serial_number"] == data["serial_number"]
        assert response.json["notes"] == data["notes"]
        assert response.json["price"] == data["price"]
        assert response.json["currency"] == data["currency"]
        assert response.json["is_reserved"] == data["is_reserved"]

    def test_item_route_delete(self):
        """
        Item update API should return the deleted Item object.
        """
        data = product_helpers.create_product_item(self.client)

        response = self.client.delete(
            url_for(
                "api.product.item.delete",
                product_id=data["product_id"],
                id=data["id"],
            )
        )
        assert response.status_code == 200
        assert response.json["product_id"] == data["product_id"]
        assert response.json["color"] == data["color"]
        assert response.json["serial_number"] == data["serial_number"]
        assert response.json["notes"] == data["notes"]
        assert response.json["price"] == data["price"]
        assert response.json["currency"] == data["currency"]
        assert response.json["is_reserved"] == data["is_reserved"]

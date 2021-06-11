from decimal import Decimal
import json
import pytest
import werkzeug
from flask import url_for

from lib.test import ViewTestMixin

from bitcoinstore.extensions import db

from test.factories import ProductFactory, ProductItemFactory


class TestProductItems(ViewTestMixin):
    create_route = "api/v1.products.items.create"
    update_route = "api/v1.products.items.update"

    def test_create_without_product_id(self):
        """ Create without product id returns 405."""
        with pytest.raises(werkzeug.routing.BuildError):
            url_for(self.create_route)

        response = self.client.post("/products/items")
        assert response.status_code == 405

    def test_create_without_required_attrs(self):
        """ Create without required item attrs returns 422."""
        product = ProductFactory.create()
        response = self.client.post(
            url_for(self.create_route, product_id=product.id)
        )

        assert response.status_code == 422

    def test_create_valid(self):
        """ Valid create should respond with a created 201."""
        product = ProductFactory.create()
        response = self.client.post(
            url_for(
                self.create_route,
                product_id=product.id,
                serial_num="12341234",
                description="",
                color="Yellow",
                unit_price_subunits=300,
                shipping_weight_kg=0.1,
                amount_in_stock=973,
            )
        )

        assert response.status_code == 201
        body = json.loads(response.data)
        assert response.headers["Location"] == url_for(
            self.update_route, product_id=product.id, id=body["id"]
        )

    def test_update_without_params(self):
        """ No-op updating should respond with success 200."""
        product = ProductFactory.create()
        product_item = ProductItemFactory.create(product=product)
        response = self.client.patch(
            url_for(
                self.update_route, product_id=product.id, id=product_item.id
            )
        )

        assert response.status_code == 200

    def test_update_valid(self):
        """ Updating should respond with success 200."""
        product_item = ProductItemFactory.create()
        response = self.client.patch(
            url_for(
                self.update_route,
                product_id=product_item.product_id,
                id=product_item.id,
                serial_num="12341234",
                description="Great!",
                color="Black",
                unit_price_subunits=20000,
                unit_price_currency="BTC",
                shipping_weight_kg=0.05,
                amount_in_stock=973,
            ),
        )

        assert response.status_code == 200

        assert product_item.serial_num == "12341234"
        assert product_item.description == "Great!"
        assert product_item.color == "Black"
        assert product_item.unit_price_subunits == 20000
        assert product_item.unit_price_currency == "BTC"
        assert product_item.shipping_weight_kg == Decimal("0.05")
        assert product_item.amount_in_stock == 973

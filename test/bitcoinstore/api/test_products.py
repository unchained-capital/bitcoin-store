from flask import url_for

from lib.test import ViewTestMixin

from test.factories import ProductFactory


class TestProducts(ViewTestMixin):
    def test_create_without_requred_params(self):
        """ Up page should respond with a success 200. """
        response = self.client.post(url_for("api/v1.products.create"))

        assert response.status_code == 422

    def test_create_valid(self):
        """ Valid create should respond with a created 201. """
        response = self.client.post(
            url_for(
                "api/v1.products.create",
                sku="12341234",
                name="Wooden Pencil, Yellow, #2, Pre-Sharpened, 30-pack",
                description="",
                color="Yellow",
                unit_price_subunits=300,
                shipping_weight_kg=0.1,
                amount_in_stock=973,
            )
        )

        assert response.status_code == 201

    def test_update_without_params(self):
        """ No-op updating should respond with success 200. """
        product = ProductFactory.create()
        print(product.id)
        response = self.client.patch(
            url_for("api/v1.products.update", id=product.id)
        )

        assert response.status_code == 200

    def test_update_valid(self):
        """ Updating should respond with success 200. """
        product = ProductFactory.create()
        print(product.id)
        response = self.client.patch(
            url_for(
                "api/v1.products.update",
                id=product.id,
            ),
            data=dict(
                sku="12341234",
                name="Pen, Black, 30-pack",
                description="Great!",
                color="Black",
                unit_price_subunits=20000,
                unit_price_currency="BTC",
                shipping_weight_kg=0.05,
                amount_in_stock=973,
            ),
        )

        assert response.status_code == 200

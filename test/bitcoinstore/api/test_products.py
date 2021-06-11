import json
from flask import url_for

from lib.test import ViewTestMixin

from test.factories import ProductFactory


class TestProducts(ViewTestMixin):
    create_route = "api/v1.products.create"
    update_route = "api/v1.products.update"

    def test_create_without_requred_params(self):
        """ Create without required attrs returns 422. """
        response = self.client.post(url_for(self.create_route))

        assert response.status_code == 422

    def test_create_valid(self):
        """ Valid create should respond with a created 201. """
        response = self.client.post(
            url_for(
                self.create_route,
                sku="12341234",
                name="Wooden Pencil, Yellow, #2, Pre-Sharpened, 30-pack",
                description="",
            )
        )

        assert response.status_code == 201
        body = json.loads(response.data)
        assert response.headers["Location"] == url_for(
            self.update_route, id=body["id"]
        )

    def test_update_without_params(self):
        """ No-op updating should respond with success 200. """
        product = ProductFactory.create()
        response = self.client.patch(url_for(self.update_route, id=product.id))

        assert response.status_code == 200

    def test_update_valid(self):
        """ Updating should respond with success 200. """
        product = ProductFactory.create()
        response = self.client.patch(
            url_for(
                self.update_route,
                id=product.id,
            ),
            data=dict(
                sku="12341234",
                name="Pen, Black, 30-pack",
                description="Great!",
            ),
        )

        assert response.status_code == 200

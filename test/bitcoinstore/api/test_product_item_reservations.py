import json
import pytest
import werkzeug
from flask import url_for

from lib.test import ViewTestMixin

from test.factories import ProductItemFactory, ProductItemReservationFactory


class TestProductItemReservations(ViewTestMixin):
    create_route = "api/v1.products.items.reservations.create"
    destroy_route = "api/v1.products.items.reservations.destroy"

    def test_create_without_product_id(self):
        """ Create without product id returns 405. """
        with pytest.raises(werkzeug.routing.BuildError):
            url_for(self.create_route)

        response = self.client.post("/products//items//reservations")
        assert response.status_code == 405

    def test_create_without_required_attrs(self):
        """ Create without required item attrs returns 422."""
        product_item = ProductItemFactory.create()
        response = self.client.post(
            url_for(
                self.create_route,
                product_id=product_item.product_id,
                product_item_id=product_item.id,
            )
        )

        assert response.status_code == 422

    def test_create_insufficient_available(self):
        """Create without sufficient items in stock should respond with
        payload too large 413.
        """
        product_item = ProductItemFactory.create(amount_in_stock=3)
        response = self.client.post(
            url_for(
                self.create_route,
                product_id=product_item.product_id,
                product_item_id=product_item.id,
                cart_id="Foo",
                amount=10,
            )
        )
        assert response.status_code == 413

    def test_create_valid(self):
        """ Valid create should respond with a created 201."""
        product_item = ProductItemFactory.create(amount_in_stock=10)
        response = self.client.post(
            url_for(
                self.create_route,
                product_id=product_item.product_id,
                product_item_id=product_item.id,
                cart_id="Foo",
                amount=2,
            )
        )

        assert response.status_code == 201
        body = json.loads(response.data)
        assert response.headers["Location"] == url_for(
            self.destroy_route,
            product_id=product_item.product_id,
            product_item_id=product_item.id,
            id=body["id"],
        )

    def test_destroy_valid(self):
        """ Destroying should respond with success 200."""
        reservation = ProductItemReservationFactory.create()
        response = self.client.delete(
            url_for(
                self.destroy_route,
                product_id=reservation.product_item.product_id,
                product_item_id=reservation.product_item_id,
                id=reservation.id,
            )
        )

        assert response.status_code == 200

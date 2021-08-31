from flask import url_for

from lib.test import ApiTestMixin
from bitcoinstore.api.models.FungibleItem import FungibleItem


f_sku = '12341234'
f_props = {
    "amount_in_stock": 973,
    "color": "Yellow",
    "description": "Wooden Pencil, Yellow, #2, Pre-Sharpened, 30-pack",
    "shipping_weight_grams": 100,
    "unit_price_cents": 300
}

nf_sku = '91919191'
nf_sn = "VIN1234134134"
nf_props = {
    "color": "Yellow",
    "description": "Motorcyle, Honda CB750F",
    "notes": "Scratches on the clearcoat on the fuel tank.",
    "price_cents": 320000,
    "shipping_weight_grams": 200000,
    "sold": False
}


class TestApi(ApiTestMixin):


    def test_post_fungible(self):
        """ Should respond with a success 200 and new fungible item. """

        response1 = self.client.post(url_for("api.post_fungible"))

        json_res1 = response1.get_json()

        # Item is set with default values, check
        assert response1.status_code == 200
        assert type(json_res1['sku']) is str
        assert type(json_res1['amount_in_stock']) is int \
            and json_res1['amount_in_stock'] == 0
        assert json_res1['color'] is None
        assert json_res1['description'] is None
        assert type(json_res1['shipping_weight_grams']) is int \
            and json_res1['shipping_weight_grams'] == 0
        assert type(json_res1['unit_price_cents']) is int \
            and json_res1['unit_price_cents'] == 0

        response2 = self.client.post(
            url_for("api.post_fungible"), json=f_props
        )

        json_res2 = response2.get_json()

        assert response2.status_code == 200
        assert type(json_res2['sku']) is str
        assert type(json_res2['amount_in_stock']) is int \
            and json_res2['amount_in_stock'] == f_props['amount_in_stock']
        assert type(json_res2['color']) is str \
            and json_res2['color'] == f_props['color']
        assert type(json_res2['description']) is str \
            and json_res2['description'] == f_props['description']
        assert type(json_res2['shipping_weight_grams']) is int \
            and json_res2['shipping_weight_grams'] == f_props['shipping_weight_grams']
        assert type(json_res2['unit_price_cents']) is int \
            and json_res2['unit_price_cents'] == f_props['unit_price_cents']


    def test_put_fungible(self):
        """
        Should respond with a success 200 for new and update request.
        Should also respond with item.
        """

        sku = f_sku

        response1 = self.client.put( url_for("api.put_fungible", sku=sku) )

        json_res1 = response1.get_json()

        # Item is set with default values, check
        assert response1.status_code == 200
        assert type(json_res1['sku']) is str
        assert type(json_res1['amount_in_stock']) is int \
            and json_res1['amount_in_stock'] == 0
        assert json_res1['color'] is None
        assert json_res1['description'] is None
        assert type(json_res1['shipping_weight_grams']) is int \
            and json_res1['shipping_weight_grams'] == 0
        assert type(json_res1['unit_price_cents']) is int \
            and json_res1['unit_price_cents'] == 0

        response2 = self.client.put(
            url_for("api.put_fungible", sku=sku),
            json=f_props
        )

        json_res2 = response2.get_json()

        assert response2.status_code == 200
        assert type(json_res2['sku']) is str \
            and json_res2['sku'] == sku
        assert type(json_res2['amount_in_stock']) is int \
            and json_res2['amount_in_stock'] == f_props['amount_in_stock']
        assert type(json_res2['color']) is str \
            and json_res2['color'] == f_props['color']
        assert type(json_res2['description']) is str \
            and json_res2['description'] == f_props['description']
        assert type(json_res2['shipping_weight_grams']) is int \
            and json_res2['shipping_weight_grams'] == f_props['shipping_weight_grams']
        assert type(json_res2['unit_price_cents']) is int \
            and json_res2['unit_price_cents'] == f_props['unit_price_cents']


    def test_post_fungible_add(self):
        """
        Should respond with a success 200.
        Should respond with item where amount_in_stock is 23 greater than DB content.
        """
        add_quantity = 23
        sku = f_sku

        item = self.db.session.query(FungibleItem).get(sku)

        original_stock = item.get_amount_in_stock()

        response = self.client.post(
            url_for("api.post_fungible_add", sku=sku, quantity=add_quantity)
        )

        json_res = response.get_json()

        assert json_res['amount_in_stock'] == original_stock + add_quantity


    def test_post_fungible_remove(self):
        """
        Should respond with a success 200.
        Should respond with item where amount_in_stock is 23 less than DB content.
        """
        remove_quantity = 23
        sku = f_sku

        item = self.db.session.query(FungibleItem).get(sku)

        original_stock = item.get_amount_in_stock()

        response = self.client.post(
            url_for("api.post_fungible_remove", sku=sku, quantity=remove_quantity)
        )

        json_res = response.get_json()

        assert json_res['amount_in_stock'] == original_stock - remove_quantity


    def test_get_fungible(self):
        """ Should respond with a success 200 and existing fungible item. """

        sku = f_sku

        item = self.db.session.query(FungibleItem).get(sku)
        db_item = item.get_summary()

        response = self.client.get( url_for("api.get_fungible", sku=sku) )
        json_res = response.get_json()

        assert response.status_code == 200
        assert json_res['sku'] == db_item['sku']
        assert json_res['amount_in_stock'] == db_item['amount_in_stock']
        assert json_res['color'] == db_item['color']
        assert json_res['description'] == db_item['description']
        assert json_res['shipping_weight_grams'] == db_item['shipping_weight_grams']
        assert json_res['unit_price_cents'] == db_item['unit_price_cents']


    def test_put_non_fungible(self):
        """
        Should respond with a success 200 for new and update request.
        Should also respond with item.
        """

        sku = nf_sku
        sn = nf_sn

        response1 = self.client.put(
            url_for("api.put_non_fungible", sku=sku, sn=sn)
        )

        json_res1 = response1.get_json()

        # Item is set with default values, check
        assert response1.status_code == 200
        assert type(json_res1['sku']) is str \
            and json_res1['sku'] == sku
        assert type(json_res1['sn']) is str \
            and json_res1['sn'] == sn
        assert json_res1['color'] is None
        assert json_res1['description'] is None
        assert json_res1['notes'] is None
        assert type(json_res1['price_cents']) is int \
            and json_res1['price_cents'] == 0
        assert type(json_res1['shipping_weight_grams']) is int \
            and json_res1['shipping_weight_grams'] == 0
        assert json_res1['sold'] == False

        response2 = self.client.put(
            url_for("api.put_non_fungible", sku=sku, sn=sn),
            json=nf_props
        )

        json_res2 = response2.get_json()

        assert response2.status_code == 200
        assert json_res2['sku'] == sku
        assert json_res2['sn'] == sn
        assert json_res2['color'] == nf_props['color']
        assert json_res2['description'] == nf_props['description']
        assert json_res2['notes'] == nf_props['notes']
        assert json_res2['price_cents'] == nf_props['price_cents']
        assert json_res2['shipping_weight_grams'] == nf_props['shipping_weight_grams']
        assert json_res2['sold'] == nf_props['sold']

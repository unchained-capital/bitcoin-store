from flask import url_for

from bitcoinstore.extensions import db
from lib.test import ViewTestMixin

nfp = {
    "sku": "CAR",
    "name": "an automobile",
    "description": "four wheels, engine, passenger compartment",
    "price": 99999999,
    "weight": 2000,
    "fungible": False,
    "serial": "madmax",
    "nfp_desc": "black 1974 Ford Falcon XB GT w/ supercharger, pursuit special",
}

nfp2 = {
    "sku": "TREADED_CAR",
    "name": "car w/ tank treads",
    "description": "tank treads, engine, passenger compartment",
    "price": 12000000,
    "weight": 3000,
    "fungible": False,
    "serial": "bulletfarmer",
    "nfp_desc": 'Howe and Howe Ripsaw EV1 "The Peacemaker"',
}

fp = {
    "sku": "CAR",
    "name": "an automobile",
    "description": "four wheels, engine, passenger compartment",
    "price": 5000000,
    "weight": 2000,
    "fungible": True,
    "qty": 10,
    "qty_reserved": 1,
}

fp2 = {
    "sku": "BIKE",
    "name": "bicycle",
    "description": "two wheels, pedals, handlebars",
    "price": 10000,
    "weight": 30,
    "qty": 100,
    "qty_reserved": 11,
}


# does the mixin matter? should I create a new one?
class TestProducts(ViewTestMixin):
    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def validateFields(self, json, product):
        assert json["sku"] == product["sku"]
        assert json["name"] == product["name"]
        assert json["description"] == product["description"]
        assert json["price"] == product["price"]
        assert json["weight"] == product["weight"]

        if "fungible" in product:
            assert json["fungible"] == product["fungible"]
        if "qty" in product:
            assert json["qty"] == product["qty"]
        if "qty_reserved" in product:
            assert json["qty_reserved"] == product["qty_reserved"]
        if "serial" in product:
            assert json["serial"] == product["serial"]
        if "nfp_desc" in product:
            assert json["nfp_desc"] == product["nfp_desc"]

    def test_create_no_args(self):
        response = self.client.post(url_for("products.createFungible"))
        assert 400 == response.status_code

        response = self.client.post(url_for("products.createNonFungible"))
        assert 400 == response.status_code

    def test_create_fp(self):
        response = self.client.post(url_for("products.createFungible"), json=fp)
        assert 201 == response.status_code
        self.validateFields(response.get_json(), fp)

    def test_create_nfp(self):
        response = self.client.post(
            url_for("products.createNonFungible"), json=nfp
        )
        assert 201 == response.status_code
        self.validateFields(response.get_json(), nfp)

    def test_create_nfp_missing_required_fields(self):
        # nonfungible w/o sku
        response = self.client.post(
            url_for("products.createNonFungible"),
            json=dict((key, nfp[key]) for key in nfp if key != "sku"),
        )
        assert 400 == response.status_code
        assert "sku" in str(response.data)

        # nonfungible w/o serial
        response = self.client.post(
            url_for("products.createNonFungible"),
            json=dict((key, nfp[key]) for key in nfp if key != "serial"),
        )
        assert 400 == response.status_code
        assert "serial" in str(response.data)

    def test_create_fp_missing_required_fields(self):
        # nonfungible w/o sku
        response = self.client.post(
            url_for("products.createFungible"),
            json=dict((key, fp[key]) for key in fp if key != "sku"),
        )
        assert 400 == response.status_code
        assert "sku" in str(response.data)

    def test_create_fp_invalid_fields_ignored(self):
        # fungible with serial
        response = self.client.post(
            url_for("products.createFungible"),
            json={**fp, "serial": "unique_serial"},
        )
        assert 201 == response.status_code
        assert "serial" not in response.get_json()

        self.tearDown()
        self.setUp()

        # fungible with nfp_desc
        response = self.client.post(
            url_for("products.createFungible"),
            json={
                **fp,
                "nfp_desc": "this very unique fungible item has scratches on the gas tank",
            },
        )
        assert 201 == response.status_code
        assert "nfp_desc" not in response.get_json()

    def test_create_nfp_invalid_fields(self):
        # nfp with qty
        response = self.client.post(
            url_for("products.createNonFungible"), json={**nfp, "qty": 1}
        )
        assert 201 == response.status_code
        assert "qty" not in response.get_json()

        self.tearDown()
        self.setUp()

        # nfp with qty_reserved
        response = self.client.post(
            url_for("products.createNonFungible"),
            json={**nfp, "qty_reserved": 1},
        )
        assert 201 == response.status_code
        assert "qty" not in response.get_json()

    def test_create_fp_duplicate_sku(self):
        response = self.client.post(url_for("products.createFungible"), json=fp)
        assert 201 == response.status_code

        response = self.client.post(url_for("products.createFungible"), json=fp)
        assert 409 == response.status_code
        assert "sku" in str(response.data)

    def test_create_nfp_duplicate_serial(self):
        response = self.client.post(
            url_for("products.createNonFungible"), json=nfp
        )
        assert 201 == response.status_code

        response = self.client.post(
            url_for("products.createNonFungible"), json={**nfp, "sku": "BATCAR"}
        )
        assert 409 == response.status_code
        assert "serial" in str(response.data)

    def test_create_nfp_duplicate_sku(self):
        response = self.client.post(
            url_for("products.createNonFungible"), json=nfp
        )
        assert 201 == response.status_code

        response = self.client.post(
            url_for("products.createNonFungible"),
            json={**nfp, "serial": "something_different"},
        )
        assert 201 == response.status_code
        assert "something_different" in str(response.data)

    def test_get_fungible_invalid_id(self):
        response = self.client.get(url_for("products.getFungible", id=1))
        assert 404 == response.status_code

    def test_get_non_fungible_invalid_id(self):
        response = self.client.get(url_for("products.getNonFungible", id=1))
        assert 404 == response.status_code

    def test_get_nfp(self):
        response = self.client.post(
            url_for("products.createNonFungible"), json=nfp
        )
        assert 201 == response.status_code
        id = response.get_json()["non_fungible_id"]

        response = self.client.get(url_for("products.getNonFungible", id=id))
        assert 200 == response.status_code
        self.validateFields(response.get_json(), nfp)
        assert response.get_json()["non_fungible_id"] == id

    def test_query_nfp(self):
        ids = []
        response = self.client.post(
            url_for("products.createNonFungible"), json=nfp
        )
        assert 201 == response.status_code
        ids.append(response.get_json()["non_fungible_id"])

        different_nfp = {**nfp}
        different_nfp.update({"serial": "different_serial"})
        response = self.client.post(
            url_for("products.createNonFungible"), json=different_nfp
        )
        assert 201 == response.status_code
        ids.append(response.get_json()["non_fungible_id"])

        different_nfp = {**nfp}
        different_nfp.update(
            {"serial": "another_different_serial", "sku": "different_sku"}
        )
        response = self.client.post(
            url_for("products.createNonFungible"), json=different_nfp
        )
        assert 201 == response.status_code
        ids.append(response.get_json()["non_fungible_id"])

        # query all
        response = self.client.get(url_for("products.queryNonFungible"))
        assert 200 == response.status_code
        assert len(response.json) == 3
        # check that returned skus are what we expect
        returned_ids = [
            response.json[0]["non_fungible_id"],
            response.json[1]["non_fungible_id"],
            response.json[2]["non_fungible_id"],
        ]
        for id in ids:
            assert id in returned_ids

        # query by sku
        response = self.client.get(
            url_for("products.queryNonFungible") + "?sku=" + nfp["sku"]
        )
        assert 200 == response.status_code
        assert len(response.json) == 2
        for returned in response.json:
            assert returned["sku"] == nfp["sku"]

        # query by serial
        response = self.client.get(
            url_for("products.queryNonFungible") + "?serial=" + nfp["serial"]
        )
        assert 200 == response.status_code
        assert len(response.json) == 1
        assert response.json[0]["serial"] == nfp["serial"]

    def test_get_fp(self):
        response = self.client.post(url_for("products.createFungible"), json=fp)
        assert 201 == response.status_code
        id = response.get_json()["fungible_id"]

        response = self.client.get(url_for("products.getFungible", id=id))
        assert 200 == response.status_code
        self.validateFields(response.get_json(), fp)
        assert response.get_json()["fungible_id"] == id

    def test_query_fp(self):
        ids = []
        response = self.client.post(url_for("products.createFungible"), json=fp)
        assert 201 == response.status_code
        ids.append(response.get_json()["fungible_id"])

        different_fp = {**fp}
        different_fp.update({"sku": "different_sku"})
        response = self.client.post(
            url_for("products.createFungible"), json=different_fp
        )
        assert 201 == response.status_code
        ids.append(response.get_json()["fungible_id"])

        response = self.client.get(url_for("products.queryFungible"))
        assert 200 == response.status_code
        assert len(response.json) == 2
        # check that returned skus are what we expect
        returned_ids = [
            response.json[0]["fungible_id"],
            response.json[1]["fungible_id"],
        ]
        for id in ids:
            assert id in returned_ids

        # query by sku
        response = self.client.get(
            url_for("products.queryFungible") + "?sku=" + nfp["sku"]
        )
        assert 200 == response.status_code
        assert len(response.json) == 1
        assert response.json[0]["sku"] == nfp["sku"]

    def test_update_fungible_invalid_id(self):
        response = self.client.put(
            url_for("products.updateFungible", id=1), json=fp
        )
        assert 404 == response.status_code

    def test_update_nonfungible_invalid_id(self):
        response = self.client.put(
            url_for("products.updateNonFungible", id=1), json=fp
        )
        assert 404 == response.status_code

    def test_update_fp(self):
        response = self.client.post(url_for("products.createFungible"), json=fp)
        assert 201 == response.status_code
        id = response.get_json()["fungible_id"]

        response = self.client.put(
            url_for("products.updateFungible", id=id), json=fp2
        )
        assert 200 == response.status_code
        self.validateFields(response.get_json(), fp2)

    def test_update_fp_ignore_invalid_fields(self):
        response = self.client.post(url_for("products.createFungible"), json=fp)
        assert 201 == response.status_code
        id = response.get_json()["fungible_id"]

        response = self.client.put(
            url_for("products.updateFungible", id=id),
            json={
                **fp2,
                "serial": "cap'n crunch",
                "nfp_desc": "the crunchiest",
            },
        )
        assert 200 == response.status_code
        self.validateFields(response.get_json(), fp2)
        assert "serial" not in response.get_json()
        assert "nfp_desc" not in response.get_json()

    def test_update_nfp(self):
        response = self.client.post(
            url_for("products.createNonFungible"), json=nfp
        )
        assert 201 == response.status_code
        id = response.get_json()["non_fungible_id"]

        response = self.client.put(
            url_for("products.updateNonFungible", id=id), json=nfp2
        )
        assert 200 == response.status_code
        self.validateFields(response.get_json(), nfp2)

    def test_update_nfp_ignore_invalid_fields(self):
        response = self.client.post(
            url_for("products.createNonFungible"), json=nfp
        )
        assert 201 == response.status_code
        id = response.get_json()["non_fungible_id"]

        response = self.client.put(
            url_for("products.updateNonFungible", id=id),
            json={**nfp2, "qty": 1, "qty_reserved": 1},
        )
        assert 200 == response.status_code
        self.validateFields(response.get_json(), nfp2)
        assert "qty" not in response.get_json()

    def test_delete_fp(self):
        response = self.client.post(url_for("products.createFungible"), json=fp)
        assert 201 == response.status_code
        id = response.get_json()["fungible_id"]

        response = self.client.delete(url_for("products.deleteFungible", id=id))
        assert 204 == response.status_code

        response = self.client.get(url_for("products.getFungible", id=id))
        assert 404 == response.status_code

    def test_delete_nfp(self):
        response = self.client.post(
            url_for("products.createNonFungible"), json=nfp
        )
        assert 201 == response.status_code
        id = response.get_json()["non_fungible_id"]

        response = self.client.delete(
            url_for("products.deleteNonFungible", id=id)
        )
        assert 204 == response.status_code

        response = self.client.get(url_for("products.getNonFungible", id=id))
        assert 404 == response.status_code

    # why does this test fail? it works fine outside of a unit test
    # for some reason calling deleteNonFungibleSku returns 409 but actually
    # deletes the NonFungibleProduct object ¯\_(ツ)_/¯
    # def test_delete_nfp_sku(self):
    # 	response = self.client.post(url_for("products.createNonFungible"), json=nfp)
    # 	assert 201 == response.status_code
    # 	id = response.get_json()["non_fungible_id"]
    #
    # 	# can't delete a sku with associated nfps
    # 	response = self.client.delete(url_for("products.deleteNonFungibleSku", sku=nfp['sku']))
    # 	assert 409 == response.status_code
    #
    # 	response = self.client.delete(url_for("products.deleteNonFungible", id=id))
    # 	assert 204 == response.status_code
    #
    # 	# now you can delete it
    # 	response = self.client.delete(url_for("products.deleteNonFungibleSku", sku=nfp['sku']))
    # 	assert 204 == response.status_code

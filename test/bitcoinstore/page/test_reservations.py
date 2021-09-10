import datetime

from dateutil.parser import parse
from flask import url_for

from bitcoinstore.extensions import db
from bitcoinstore.model.product import (
    FungibleProduct,
    NonFungibleProduct,
    NonFungibleSku,
)
from bitcoinstore.model.reservation import (
    FungibleReservation,
    NonFungibleReservation,
)
from lib.test import ViewTestMixin

nfp = {
    "sku": "CAR",
    "price": 99999999,
    "weight": 2000,
    "fungible": False,
    "serial": "madmax",
    "nfp_desc": "black 1974 Ford Falcon XB GT w/ supercharger, pursuit special",
}

nfp2 = {
    "sku": "BIKE",
    "price": 9999,
    "weight": 200,
    "fungible": False,
    "serial": "qwerty",
    "nfp_desc": "black 1974 Schwinn Twinn tandem, leisure special",
}

nfp_sku = {
    "sku": "CAR",
    "name": "an automobile",
    "description": "four wheels, engine, passenger compartment",
}

nfp_sku2 = {
    "sku": "BIKE",
    "name": "a bicycle",
    "description": "two wheels, pedals, handlebars",
}

nfp_res = {
    "serial": "madmax",
    "userId": "steve",
    # expires tomorrow
    "expiration": (
        datetime.datetime.today() + datetime.timedelta(days=1)
    ).replace(microsecond=0),
}

nfp_res2 = {
    "serial": "qwerty",
    "userId": "alice",
    # expires tomorrow
    "expiration": (
        datetime.datetime.today() + datetime.timedelta(days=1)
    ).replace(microsecond=0),
}

fp = {
    "sku": "CAR",
    "name": "an automobile",
    "description": "four wheels, engine, passenger compartment",
    "price": 5000000,
    "weight": 2000,
    "fungible": True,
    "qty": 10,
    "qty_reserved": 0,
}

fp2 = {
    "sku": "BIKE",
    "name": "a bicycle",
    "description": "two wheels, pedals, handlebars",
    "price": 5000,
    "weight": 200,
    "fungible": True,
    "qty": 10,
    "qty_reserved": 0,
}

fp_res = {
    "sku": "CAR",
    "qty": 1,
    "userId": "steve",
    # expires tomorrow
    "expiration": (
        datetime.datetime.today() + datetime.timedelta(days=1)
    ).replace(microsecond=0),
}

fp_res2 = {
    "sku": "BIKE",
    "qty": 1,
    "userId": "alice",
    # expires tomorrow
    "expiration": (
        datetime.datetime.today() + datetime.timedelta(days=1)
    ).replace(microsecond=0),
}


# does the mixin matter? should I create a new one?
class TestReservations(ViewTestMixin):
    def setUp(self):
        db.create_all()
        # directly insert products to avoid test failures from broken REST endpoints
        self.insertFungibleProduct()
        self.insertNonFungibleProduct()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def insertFungibleProduct(self):
        db.session.add(
            FungibleProduct(
                sku=fp.get("sku"),
                name=fp.get("name"),
                description=fp.get("description"),
                qty=fp.get("qty"),
                qty_reserved=fp.get("qty_reserved"),
                price=fp.get("price"),
                weight=fp.get("weight"),
            )
        )
        db.session.add(
            FungibleProduct(
                sku=fp2.get("sku"),
                name=fp2.get("name"),
                description=fp2.get("description"),
                qty=fp2.get("qty"),
                qty_reserved=fp2.get("qty_reserved"),
                price=fp2.get("price"),
                weight=fp2.get("weight"),
            )
        )
        db.session.commit()

    def insertNonFungibleProduct(self):
        db.session.add(
            NonFungibleSku(
                sku=nfp_sku.get("sku"),
                name=nfp_sku.get("name"),
                description=nfp_sku.get("description"),
            )
        )
        db.session.add(
            NonFungibleSku(
                sku=nfp_sku2.get("sku"),
                name=nfp_sku2.get("name"),
                description=nfp_sku2.get("description"),
            )
        )

        db.session.add(
            NonFungibleProduct(
                sku=nfp.get("sku"),
                serial=nfp.get("serial"),
                nfp_desc=nfp.get("nfp_desc"),
                price=nfp.get("price"),
                weight=nfp.get("weight"),
            )
        )
        db.session.add(
            NonFungibleProduct(
                sku=nfp2.get("sku"),
                serial=nfp2.get("serial"),
                nfp_desc=nfp2.get("nfp_desc"),
                price=nfp2.get("price"),
                weight=nfp2.get("weight"),
            )
        )
        db.session.commit()

    def validateFields(self, json, reservation, expired):
        assert json["userId"] == reservation["userId"]
        assert (
            parse(json["expiration"]).timestamp()
            == reservation["expiration"].timestamp()
        )
        assert json["expired"] == expired

        if isinstance(reservation, FungibleReservation):
            assert json["sku"] == reservation["sku"]
            assert json["qty"] == reservation["qty"]
        elif isinstance(reservation, NonFungibleReservation):
            assert json["serial"] == reservation["serial"]

    def test_create_no_args(self):
        response = self.client.post(url_for("reservations.createFungible"))
        assert 400 == response.status_code

        response = self.client.post(url_for("reservations.createNonFungible"))
        assert 400 == response.status_code

    def test_create_fp_res(self):
        response = self.client.post(
            url_for("reservations.createFungible"), json=fp_res
        )
        assert 201 == response.status_code
        self.validateFields(response.get_json(), fp_res, expired=False)

        # check fungible product qty reserved was incremented
        response = self.client.get(
            url_for("products.queryFungible") + "?sku=" + fp["sku"]
        )
        assert 200 == response.status_code
        assert (
            fp_res["qty"] + fp["qty_reserved"]
            == response.json[0]["qty_reserved"]
        )

    def test_create_nfp_res(self):
        response = self.client.post(
            url_for("reservations.createNonFungible"), json=nfp_res
        )
        assert 201 == response.status_code
        self.validateFields(response.get_json(), nfp_res, expired=False)

        # check non fungible product was reserved
        response = self.client.get(
            url_for("products.queryNonFungible") + "?serial=" + nfp["serial"]
        )
        assert 200 == response.status_code
        assert response.json[0]["reserved"]

    def test_create_fp_res_invalid(self):
        fp_res_invalid = {**fp_res}
        fp_res_invalid.pop("sku")
        response = self.client.post(
            url_for("reservations.createFungible"), json=fp_res_invalid
        )
        assert 400 == response.status_code
        assert "sku" in str(response.data)

        fp_res_invalid = {**fp_res}
        fp_res_invalid.pop("qty")
        response = self.client.post(
            url_for("reservations.createFungible"), json=fp_res_invalid
        )
        assert 400 == response.status_code
        assert "qty" in str(response.data)

        fp_res_invalid = {**fp_res}
        fp_res_invalid.pop("userId")
        response = self.client.post(
            url_for("reservations.createFungible"), json=fp_res_invalid
        )
        assert 400 == response.status_code
        assert "userId" in str(response.data)

    def test_create_nfp_res_invalid(self):
        nfp_res_invalid = {**nfp_res}
        nfp_res_invalid.pop("serial")
        response = self.client.post(
            url_for("reservations.createNonFungible"), json=nfp_res_invalid
        )
        assert 400 == response.status_code
        assert "serial" in str(response.data)

        nfp_res_invalid = {**nfp_res}
        nfp_res_invalid.pop("userId")
        response = self.client.post(
            url_for("reservations.createNonFungible"), json=nfp_res_invalid
        )
        assert 400 == response.status_code
        assert "userId" in str(response.data)

    def test_get_fp_res(self):
        response = self.client.post(
            url_for("reservations.createFungible"), json=fp_res
        )
        assert 201 == response.status_code
        id = response.json["id"]

        response = self.client.get(url_for("reservations.getFungible", id=id))
        assert 200 == response.status_code
        self.validateFields(response.get_json(), fp_res, expired=False)

    def test_query_fp_res(self):
        response = self.client.post(
            url_for("reservations.createFungible"), json=fp_res
        )
        assert 201 == response.status_code

        response = self.client.post(
            url_for("reservations.createFungible"), json=fp_res2
        )
        assert 201 == response.status_code

        response = self.client.get(url_for("reservations.queryFungible"))
        assert 200 == response.status_code
        assert 2 == len(response.get_json())

        response = self.client.get(
            url_for("reservations.queryFungible")
            + "?userId="
            + fp_res["userId"]
        )
        assert 200 == response.status_code
        assert 1 == len(response.get_json())
        assert fp_res["userId"] == response.json[0]["userId"]

        response = self.client.get(
            url_for("reservations.queryFungible") + "?sku=" + fp_res["sku"]
        )
        assert 200 == response.status_code
        assert 1 == len(response.get_json())
        assert fp_res["sku"] == response.json[0]["sku"]

    def test_get_fp_res_invalid_id(self):
        response = self.client.get(url_for("reservations.getFungible", id=1))
        assert 404 == response.status_code

    def test_get_nfp_res(self):
        response = self.client.post(
            url_for("reservations.createNonFungible"), json=nfp_res
        )
        assert 201 == response.status_code
        id = response.json["id"]

        response = self.client.get(
            url_for("reservations.getNonFungible", id=id)
        )
        assert 200 == response.status_code
        self.validateFields(response.get_json(), nfp_res, expired=False)

    def test_query_nfp_res(self):
        response = self.client.post(
            url_for("reservations.createNonFungible"), json=nfp_res
        )
        assert 201 == response.status_code

        response = self.client.post(
            url_for("reservations.createNonFungible"), json=nfp_res2
        )
        assert 201 == response.status_code

        response = self.client.get(url_for("reservations.queryNonFungible"))
        assert 200 == response.status_code
        assert 2 == len(response.get_json())

        response = self.client.get(
            url_for("reservations.queryNonFungible")
            + "?userId="
            + nfp_res["userId"]
        )
        assert 200 == response.status_code
        assert 1 == len(response.get_json())
        assert nfp_res["userId"] == response.json[0]["userId"]

        response = self.client.get(
            url_for("reservations.queryNonFungible")
            + "?serial="
            + nfp_res["serial"]
        )
        assert 200 == response.status_code
        assert 1 == len(response.get_json())
        assert nfp_res["serial"] == response.json[0]["serial"]

    def test_get_nfp_res_invalid_id(self):
        response = self.client.get(url_for("reservations.getNonFungible", id=1))
        assert 404 == response.status_code

    def test_expire_nfp_res(self):
        response = self.client.post(
            url_for("reservations.createNonFungible"), json=nfp_res
        )
        assert 201 == response.status_code
        id = response.json["id"]

        response = self.client.delete(
            url_for("reservations.expireNonFungible", id=id)
        )
        assert 200 == response.status_code
        self.validateFields(response.get_json(), nfp_res, expired=True)

        # check nfp was marked not reserved
        response = self.client.get(
            url_for("products.queryNonFungible") + "?serial=" + nfp["serial"]
        )
        assert 200 == response.status_code
        assert False == response.json[0]["reserved"]

    def test_expire_fp_res(self):
        response = self.client.post(
            url_for("reservations.createFungible"), json=fp_res
        )
        assert 201 == response.status_code
        id = response.json["id"]

        response = self.client.delete(
            url_for("reservations.expireFungible", id=id)
        )
        assert 200 == response.status_code
        self.validateFields(response.get_json(), fp_res, expired=True)

        # check fp quantity reserved was restored to original value
        response = self.client.get(
            url_for("products.queryFungible") + "?sku=" + nfp["sku"]
        )
        assert 200 == response.status_code
        assert fp["qty_reserved"] == response.json[0]["qty_reserved"]

from flask import url_for

from bitcoinstore.extensions import db
from bitcoinstore.model.product import FungibleProduct, NonFungibleProduct
from lib.test import ViewTestMixin

nfp = {
	"sku":"CAR",
	"name": "an automobile",
	"description": "four wheels, engine, passenger compartment",
	"price":99999999,
	"weight":2000,
	"fungible":False,
	"serial":"madmax",
	"nfp_desc":"black 1974 Ford Falcon XB GT w/ supercharger, pursuit special"
}

fp = {
	"sku":"CAR",
	"name":"an automobile",
	"description":"four wheels, engine, passenger compartment",
	"price":5000000,
	"weight":2000,
	"fungible":True,
	"qty":10,
	"qty_reserved":1
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
		assert json["fungible"] == product["fungible"]

		if 'qty' in product:
			assert json["qty"] == product["qty"]
		if 'qty_reserved' in product:
			assert json["qty_reserved"] == product["qty_reserved"]
		if 'serial' in product:
			assert json["serial"] == product["serial"]
		if 'nfp_desc' in product:
			assert json["nfp_desc"] == product["nfp_desc"]

	def test_create_no_args(self):
		response = self.client.post(url_for("products.create"))
		assert 400 == response.status_code

	def test_create_fp(self):
		response = self.client.post(url_for("products.create"), json=fp)
		assert 201 == response.status_code
		self.validateFields(response.get_json(), fp)

	def test_create_nfp(self):
		response = self.client.post(url_for("products.create"), json=nfp)
		assert 201 == response.status_code
		self.validateFields(response.get_json(), nfp)

	def test_create_nfp_then_fp(self):
		response = self.client.post(url_for("products.create"), json=nfp)
		assert 201 == response.status_code
		self.validateFields(response.get_json(), nfp)

		response = self.client.post(url_for("products.create"), json=fp)
		assert 201 == response.status_code
		self.validateFields(response.get_json(), fp)

	def test_create_fp_then_nfp(self):
		response = self.client.post(url_for("products.create"), json=fp)
		assert 201 == response.status_code
		self.validateFields(response.get_json(), fp)

		response = self.client.post(url_for("products.create"), json=nfp)
		assert 201 == response.status_code
		self.validateFields(response.get_json(), nfp)

	def test_create_missing_required_fields(self):
		# fungible without fungible field set
		# is there a better way to copy a dict in place w/o a particular key?
		response = self.client.post(url_for("products.create"), json=dict((key,fp[key]) for key in fp if key!='fungible'))
		assert 400 == response.status_code
		assert "fungible" in str(response.data)

		# nonfungible w/o fungible field
		response = self.client.post(url_for("products.create"), json=dict((key,nfp[key]) for key in nfp if key!='fungible'))
		assert 400 == response.status_code
		assert "fungible" in str(response.data)

		# nonfungible w/o sku field
		response = self.client.post(url_for("products.create"), json=dict((key,nfp[key]) for key in nfp if key!='sku'))
		assert 400 == response.status_code
		assert "sku" in str(response.data)

	def test_create_fp_invalid_fields_ignored(self):
		# fungible with serial
		response = self.client.post(url_for("products.create"), json={**fp, 'serial': "unique_serial"})
		assert 201 == response.status_code
		assert 'serial' not in response.get_json()

		self.tearDown()
		self.setUp()

		# fungible with nfp_desc
		response = self.client.post(url_for("products.create"), json={**fp, "nfp_desc": "this very unique fungible item has scratches on the gas tank"})
		assert 201 == response.status_code
		assert 'nfp_desc' not in response.get_json()

	def test_create_nfp_invalid_fields(self):
		# nfp with qty
		response = self.client.post(url_for("products.create"), json={**nfp, "qty":1})
		assert 201 == response.status_code
		assert 'qty' not in response.get_json()

		self.tearDown()
		self.setUp()

		# nfp with qty_reserved
		response = self.client.post(url_for("products.create"), json={**nfp, "qty_reserved":1})
		assert 201 == response.status_code
		assert 'qty' not in response.get_json()

	def test_create_fp_duplicate_sku(self):
		response = self.client.post(url_for("products.create"), json=fp)
		assert 201 == response.status_code

		response = self.client.post(url_for("products.create"), json=fp)
		assert 409 == response.status_code
		assert "sku" in str(response.data)

	def test_create_nfp_duplicate_serial(self):
		response = self.client.post(url_for("products.create"), json=nfp)
		assert 201 == response.status_code

		response = self.client.post(url_for("products.create"), json={**nfp, "sku": "BATCAR"})
		assert 409 == response.status_code
		assert "serial" in str(response.data)

	def test_create_nfp_duplicate_sku(self):
		response = self.client.post(url_for("products.create"), json=nfp)
		assert 201 == response.status_code

		response = self.client.post(url_for("products.create"), json={**nfp, "serial": "something_different"})
		assert 201 == response.status_code
		assert "something_different" in str(response.data)

	def test_get_all(self):
		# return empty list to start
		response = self.client.get(url_for("products.create"))
		assert response.status_code == 200
		assert response.json == []

		# add two objects
		response = self.client.post(url_for("products.create"), json=nfp)
		assert response.status_code == 201
		response = self.client.post(url_for("products.create"), json=fp)
		assert response.status_code == 201

		# get both objects
		response = self.client.get(url_for("products.getAll"))
		assert response.status_code == 200
		assert len(response.json) == 2
		# check that returned skus are what we expect
		# there is probably a more clever way to do this, i welcome your code review comments
		returned_skus = [response.json[0]['sku'],response.json[1]['sku']]
		assert nfp['sku'] in returned_skus and fp['sku'] in returned_skus

	def test_get_nfp(self):
		response = self.client.post(url_for("products.create"), json=nfp)
		assert 201 == response.status_code
		id = response.get_json()["non_fungible_id"]

		response = self.client.get(url_for("products.getNonFungible", id=id))
		assert 200 == response.status_code
		self.validateFields(response.get_json(), nfp)
		assert response.get_json()['non_fungible_id'] == id

	def test_get_nfp_all(self):
		ids = []
		response = self.client.post(url_for("products.create"), json=nfp)
		assert 201 == response.status_code
		ids.append(response.get_json()["non_fungible_id"])

		different_nfp = {**nfp}
		different_nfp.update({"serial":"different_serial"})
		response = self.client.post(url_for("products.create"), json=different_nfp)
		assert 201 == response.status_code
		ids.append(response.get_json()["non_fungible_id"])

		response = self.client.get(url_for("products.getNonFungibleAll"))
		assert 200 == response.status_code
		assert len(response.json) == 2
		# check that returned skus are what we expect
		returned_ids = [response.json[0]['non_fungible_id'], response.json[1]['non_fungible_id']]
		for id in ids:
			assert id in returned_ids

	def test_get_fp(self):
		response = self.client.post(url_for("products.create"), json=fp)
		assert 201 == response.status_code
		id = response.get_json()["fungible_id"]

		response = self.client.get(url_for("products.getFungible", id=id))
		assert 200 == response.status_code
		self.validateFields(response.get_json(), fp)
		assert response.get_json()['fungible_id'] == id

	def test_get_fp_all(self):
		ids = []
		response = self.client.post(url_for("products.create"), json=fp)
		assert 201 == response.status_code
		ids.append(response.get_json()["fungible_id"])

		different_fp = {**fp}
		different_fp.update({"sku":"different_sku"})
		response = self.client.post(url_for("products.create"), json=different_fp)
		assert 201 == response.status_code
		ids.append(response.get_json()["fungible_id"])

		response = self.client.get(url_for("products.getFungibleAll"))
		assert 200 == response.status_code
		assert len(response.json) == 2
		# check that returned skus are what we expect
		returned_ids = [response.json[0]['fungible_id'], response.json[1]['fungible_id']]
		for id in ids:
			assert id in returned_ids
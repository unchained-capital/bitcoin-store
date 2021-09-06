from flask import url_for

from lib.test import ViewTestMixin

nfp = {
	"sku":"BATMOBILE",
	"name":"batmobile",
	"description":"badass superhero car",
	"price":99999999,
	"weight":2000,
	"fungible":False,
	"serial":"BAT-MOBILE",
	"nfp_desc":"One of a kind super car"
}

fp = {
	"sku":"BATSTICKER",
	"name":"batman sticker",
	"description":"logo on front, sticky stuff on back",
	"price":500,
	"weight":10,
	"fungible":True,
	"qty":100,
	"qty_reserved":1
}

# does the mixin matter? should I create a new one?
class TestProducts(ViewTestMixin):
	def test_create_no_args(self):
		response = self.client.post(url_for("products.create"))
		assert 400 == response.status_code

	def test_create_fp(self):
		response = self.client.post(url_for("products.create"), json=fp)

		assert 201 == response.status_code
		assert response.get_json()["sku"] == fp["sku"]
		assert response.get_json()["name"] == fp["name"]
		assert response.get_json()["description"] == fp["description"]
		assert response.get_json()["price"] == fp["price"]
		assert response.get_json()["weight"] == fp["weight"]
		assert response.get_json()["fungible"] == fp["fungible"]
		assert response.get_json()["qty"] == fp["qty"]
		assert response.get_json()["qty_reserved"] == fp["qty_reserved"]

	def test_create_nfp(self):
		response = self.client.post(url_for("products.create"), json=nfp)

		assert 201 == response.status_code
		assert response.get_json()["sku"] == nfp["sku"]
		assert response.get_json()["name"] == nfp["name"]
		assert response.get_json()["description"] == nfp["description"]
		assert response.get_json()["price"] == nfp["price"]
		assert response.get_json()["weight"] == nfp["weight"]
		assert response.get_json()["fungible"] == nfp["fungible"]
		assert response.get_json()["serial"] == nfp["serial"]
		assert response.get_json()["nfp_desc"] == nfp["nfp_desc"]

	def test_create_no_fungible_value(self):
		# fungible without fungible field set
		# is there a better way to copy a dict in place w/o a particular key?
		response = self.client.post(url_for("products.create"), json=dict((key,fp[key]) for key in fp if key!='fungible'))
		assert 400 == response.status_code
		assert "fungible" in str(response.data)

		# nonfungible without fungible field set
		response = self.client.post(url_for("products.create"), json=dict((key,nfp[key]) for key in nfp if key!='fungible'))
		assert 400 == response.status_code
		assert "fungible" in str(response.data)

	def test_create_fp_invalid_fields(self):
		# fungible with serial
		response = self.client.post(url_for("products.create"), json={**fp, 'serial': "unique_serial"})
		assert 400 == response.status_code
		assert "serial" in str(response.data)

		# fungible with nfp_desc
		response = self.client.post(url_for("products.create"), json={**fp, "nfp_desc": "this very unique fungible item has scratches on the gas tank"})
		assert 400 == response.status_code
		assert "nfp_desc" in str(response.data)

	def test_create_nfp_invalid_fields(self):
		# nfp with qty
		response = self.client.post(url_for("products.create"), json={**nfp, "qty":1})
		assert 400 == response.status_code
		assert "qty" in str(response.data)

		# nfp with qty_reserved
		response = self.client.post(url_for("products.create"), json={**nfp, "qty_reserved":1})
		assert 400 == response.status_code
		assert "qty_reserved" in str(response.data)

	def test_create_fp_duplicate_sku(self):
		response = self.client.post(url_for("products.create"), json=fp)
		assert 201 == response.status_code

		response = self.client.post(url_for("products.create"), json=fp)
		assert 409 == response.status_code
		assert "sku" in str(response.data)

	def test_create_nfp_duplicate_serial(self):
		response = self.client.post(url_for("products.create"), json=nfp)
		assert 201 == response.status_code

		# duplicate serial
		response = self.client.post(url_for("products.create"), json={**nfp, "sku": "BATCAR"})
		assert 409 == response.status_code
		assert "serial" in str(response.data)

	def test_create_nfp_duplicate_sku(self):
		response = self.client.post(url_for("products.create"), json=nfp)
		assert 201 == response.status_code

		# duplicate sku
		response = self.client.post(url_for("products.create"), json={**nfp, "serial": "something_different"})
		assert 409 == response.status_code
		assert "sku" in str(response.data)

	def test_get_all(self):
		response = self.client.get(url_for("products.create"))
		assert response.status_code == 200
		assert response.json == []

		self.client.post(url_for("products.create"), json=nfp)
		self.client.post(url_for("products.create"), json=fp)
		response = self.client.get(url_for("products.create"))
		assert response.status_code == 200
		assert len(response.json) == 2
		# check that returned skus are what we expect
		returned_skus = [response.json[0]['sku'],response.json[1]['sku']]
		assert nfp['sku'] in returned_skus and fp['sku'] in returned_skus
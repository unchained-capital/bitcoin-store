from bitcoinstore.extensions import db


class Product(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    sku = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String)
    unit_price_subunits = db.Column(db.Integer, nullable=False)
    unit_price_currency = db.Column(db.String(3), nullable=False)
    shipping_weight_kg = db.Column(db.Numeric)

from bitcoinstore.extensions import db


class Product(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    sku = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)

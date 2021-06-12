from bitcoinstore.extensions import db


class Product(db.Model):
    """Records an product type.
    Specific stocked items and variants are recorded under associated
    ProductItem records.
    """

    id = db.Column(db.BigInteger, primary_key=True)
    sku = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)

    items = db.relationship("ProductItem", back_populates="product")

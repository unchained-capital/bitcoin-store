from bitcoinstore.extensions import db
from .product import Product


class ProductItem(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    product_id = db.Column(
        db.BigInteger, db.ForeignKey(Product.id), nullable=False
    )

    serial_num = db.Column(db.String)
    description = db.Column(db.Text)
    color = db.Column(db.String)
    unit_price_subunits = db.Column(db.Integer, nullable=False)
    unit_price_currency = db.Column(db.String(3), nullable=False)
    shipping_weight_kg = db.Column(db.Numeric)
    amount_in_stock = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.Index("index_serial_num", "product_id", "serial_num", unique=True),
    )
